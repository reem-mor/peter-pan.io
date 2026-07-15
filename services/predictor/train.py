"""Predictor training script — the ML rubric deliverable (pytorch-predictor skill).

Runs end-to-end with one command::

    python train.py [--seed 42] [--samples-per-class 50]

Backbone choice (documented per the skill): there is no meaningful public
pretrained backbone for 64-point univariate ops-metric windows (declared
deviation #2 swapped images for metric windows), so transfer learning is done
within the domain — phase 1 pretrains a small 1D-CNN encoder self-supervised
(window reconstruction, no labels), phase 2 freezes that backbone and
fine-tunes only the linear classification head on the six-class task. That is
the same frozen-backbone/replaced-head structure as the course's
ImageNet-transfer exercise, without pretending an image backbone applies.

Everything is seeded (torch / random); the dataset is synthetic, generated
in-process, and reproducible from the repo alone. Stop criterion: fixed epoch
budgets (no early stopping) — deterministic and honest about compute.

Outputs (committed artifacts):
- ``predictor_service/artifacts/predictor.pth`` — head + frozen-backbone weights
- ``predictor_service/artifacts/metrics.json`` — test accuracy, per-class
  precision/recall, confusion matrix, threshold, per-class counts, honesty notes
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import torch
import torch.nn as nn

from predictor_service.torch_classifier import (
    CLASS_ORDER,
    DEFAULT_CONFIDENCE_THRESHOLD,
    _build_model,
    preprocess,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "predictor_service" / "artifacts"

PRETRAIN_EPOCHS = 120
HEAD_EPOCHS = 400
LEARNING_RATE = 5e-3
# Candidate softmax-max floors evaluated on the validation set; the chosen
# value (and the val numbers behind it) land in metrics.json.
THRESHOLD_GRID = (0.5, 0.6, 0.7, 0.8)


# ── Synthetic data ────────────────────────────────────────────────────────────
# Each class has a distinct window *shape*; levels/lengths vary so the model
# must learn shape, not scale (serving z-normalizes every window anyway).


def _noise(rng: random.Random, n: int, scale: float) -> list[float]:
    return [rng.gauss(0.0, scale) for _ in range(n)]


def _make_window(rng: random.Random, incident_class: str) -> list[float]:
    # Two length regimes: short windows mirror the 7-point service fixture
    # windows (resampling smooths them into different shapes than long ones),
    # long windows mirror scraped metric ranges.
    n = rng.randint(7, 20) if rng.random() < 0.35 else rng.randint(24, 120)
    base = rng.uniform(5.0, 100.0)
    t = [i / (n - 1) for i in range(n)]
    noise = _noise(rng, n, base * 0.01)

    if incident_class == "normal":
        return [base + noise[i] * rng.uniform(1.0, 3.0) for i in range(n)]
    if incident_class == "cpu_saturation":
        # Sigmoid rise onto a sustained ceiling plateau.
        ceiling = base * rng.uniform(1.8, 3.0)
        t0, k = rng.uniform(0.2, 0.5), rng.uniform(12.0, 25.0)
        return [
            base + (ceiling - base) / (1.0 + math.exp(-k * (t[i] - t0))) + noise[i]
            for i in range(n)
        ]
    if incident_class == "memory_leak":
        # Monotonic ramp, no plateau, tiny jitter.
        slope = rng.uniform(0.5, 1.8)
        return [base * (1.0 + slope * t[i]) + noise[i] for i in range(n)]
    if incident_class == "db_lock_contention":
        # Baseline with repeated short spike bursts returning to baseline.
        window = [base + noise[i] for i in range(n)]
        for _ in range(rng.randint(3, 6)):
            start = rng.randint(0, n - 4)
            height = base * rng.uniform(0.6, 2.0)
            for j in range(start, min(start + rng.randint(2, 4), n)):
                window[j] += height
        return window
    if incident_class == "replication_lag":
        # Staircase: lag accumulates in discrete steps and never recovers.
        window, level = [], base
        max_steps = max(2, min(6, (n - 4) // 2))
        steps = sorted(rng.sample(range(2, n - 1), k=rng.randint(2, max_steps)))
        for i in range(n):
            if steps and i >= steps[0]:
                level += base * rng.uniform(0.3, 0.8)
                steps.pop(0)
            window.append(level + noise[i])
        return window
    # error_rate_spike: quiet baseline, one sudden late sustained jump.
    jump_at = rng.randint(int(n * 0.55), n - 3)
    height = base * rng.uniform(2.0, 5.0)
    return [
        base + noise[i] + (height if i >= jump_at else 0.0) for i in range(n)
    ]


def build_dataset(
    rng: random.Random, samples_per_class: int
) -> tuple[list[list[float]], list[int]]:
    windows: list[list[float]] = []
    labels: list[int] = []
    for label, incident_class in enumerate(CLASS_ORDER):
        for _ in range(samples_per_class):
            windows.append(_make_window(rng, incident_class))
            labels.append(label)
    return windows, labels


def stratified_split(
    rng: random.Random, labels: list[int]
) -> tuple[list[int], list[int], list[int]]:
    """70/15/15 per class, shuffled by the run seed."""
    train, val, test = [], [], []
    for label in range(len(CLASS_ORDER)):
        indices = [i for i, y in enumerate(labels) if y == label]
        rng.shuffle(indices)
        n_train = round(len(indices) * 0.70)
        n_val = round(len(indices) * 0.15)
        train += indices[:n_train]
        val += indices[n_train : n_train + n_val]
        test += indices[n_train + n_val :]
    rng.shuffle(train)
    return train, val, test


def _batch(windows: list[list[float]], indices: list[int]) -> torch.Tensor:
    return torch.cat([preprocess(windows[i]) for i in indices], dim=0)


# ── Training phases ───────────────────────────────────────────────────────────


def pretrain_encoder(model: nn.Module, x_train: torch.Tensor) -> None:
    """Phase 1 — self-supervised reconstruction pretraining of the backbone."""
    decoder = nn.Linear(128, x_train.shape[-1])
    params = list(model.encoder.parameters()) + list(decoder.parameters())
    optimizer = torch.optim.Adam(params, lr=LEARNING_RATE)
    loss_fn = nn.MSELoss()
    target = x_train.squeeze(1)
    for epoch in range(1, PRETRAIN_EPOCHS + 1):
        optimizer.zero_grad()
        loss = loss_fn(decoder(model.encoder(x_train)), target)
        loss.backward()
        optimizer.step()
        print(f"[pretrain] epoch {epoch:02d}/{PRETRAIN_EPOCHS} recon_loss={loss:.4f}")


def train_head(
    model: nn.Module,
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_val: torch.Tensor,
    y_val: torch.Tensor,
) -> None:
    """Phase 2 — backbone frozen, only the linear head learns."""
    for param in model.encoder.parameters():
        param.requires_grad = False
    optimizer = torch.optim.Adam(model.head.parameters(), lr=LEARNING_RATE)
    loss_fn = nn.CrossEntropyLoss()
    for epoch in range(1, HEAD_EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        loss = loss_fn(model(x_train), y_train)
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            val_logits = model(x_val)
            val_loss = loss_fn(val_logits, y_val)
            val_acc = float((val_logits.argmax(1) == y_val).float().mean())
        print(
            f"[head] epoch {epoch:02d}/{HEAD_EPOCHS} train_loss={loss:.4f} "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}"
        )


# ── Evaluation ────────────────────────────────────────────────────────────────


def threshold_report(
    model: nn.Module, x_val: torch.Tensor, y_val: torch.Tensor
) -> tuple[float, dict[str, dict[str, float]]]:
    """Coverage (share answered) and accuracy-on-answered per candidate floor."""
    with torch.no_grad():
        probs = torch.softmax(model(x_val), dim=1)
    conf, pred = probs.max(dim=1)
    report: dict[str, dict[str, float]] = {}
    for threshold in THRESHOLD_GRID:
        answered = conf >= threshold
        coverage = float(answered.float().mean())
        accuracy = (
            float((pred[answered] == y_val[answered]).float().mean())
            if int(answered.sum())
            else 0.0
        )
        report[f"{threshold:.1f}"] = {
            "coverage": round(coverage, 4),
            "accuracy_on_answered": round(accuracy, 4),
        }
    # Keep the skill's 0.6 starting floor unless a stricter floor buys accuracy
    # without dropping coverage below 90% — the val numbers are all recorded.
    chosen = DEFAULT_CONFIDENCE_THRESHOLD
    for threshold in THRESHOLD_GRID:
        entry = report[f"{threshold:.1f}"]
        best = report[f"{chosen:.1f}"]
        if (
            entry["coverage"] >= 0.90
            and entry["accuracy_on_answered"] > best["accuracy_on_answered"]
        ):
            chosen = threshold
    return chosen, report


def evaluate(
    model: nn.Module, x_test: torch.Tensor, y_test: torch.Tensor
) -> dict:
    with torch.no_grad():
        pred = model(x_test).argmax(dim=1)
    n_classes = len(CLASS_ORDER)
    confusion = [[0] * n_classes for _ in range(n_classes)]
    for true, guessed in zip(y_test.tolist(), pred.tolist()):
        confusion[true][guessed] += 1
    per_class = {}
    for i, name in enumerate(CLASS_ORDER):
        tp = confusion[i][i]
        fp = sum(confusion[r][i] for r in range(n_classes)) - tp
        fn = sum(confusion[i]) - tp
        per_class[name] = {
            "precision": round(tp / (tp + fp), 4) if tp + fp else 0.0,
            "recall": round(tp / (tp + fn), 4) if tp + fn else 0.0,
            "support": tp + fn,
        }
    accuracy = float((pred == y_test).float().mean())
    return {
        "test_accuracy": round(accuracy, 4),
        "per_class": per_class,
        "confusion_matrix": {"class_order": list(CLASS_ORDER), "rows": confusion},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples-per-class", type=int, default=50)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)

    windows, labels = build_dataset(rng, args.samples_per_class)
    train_idx, val_idx, test_idx = stratified_split(rng, labels)
    x_train, y_train = _batch(windows, train_idx), torch.tensor(
        [labels[i] for i in train_idx]
    )
    x_val, y_val = _batch(windows, val_idx), torch.tensor(
        [labels[i] for i in val_idx]
    )
    x_test, y_test = _batch(windows, test_idx), torch.tensor(
        [labels[i] for i in test_idx]
    )
    print(
        f"dataset: {len(windows)} samples "
        f"({args.samples_per_class}/class, balanced — unweighted CE loss), "
        f"split {len(train_idx)}/{len(val_idx)}/{len(test_idx)} train/val/test"
    )

    model = _build_model(len(CLASS_ORDER))
    pretrain_encoder(model, x_train)
    train_head(model, x_train, y_train, x_val, y_val)
    model.eval()

    threshold, thresholds_val = threshold_report(model, x_val, y_val)
    metrics = evaluate(model, x_test, y_test)
    metrics.update(
        {
            "confidence_threshold": threshold,
            "threshold_val_report": thresholds_val,
            "seed": args.seed,
            "dataset": {
                "samples_per_class": args.samples_per_class,
                "classes": list(CLASS_ORDER),
                "split": "70/15/15 stratified by seed",
            },
            "training": {
                "backbone": "1D-CNN encoder, self-supervised reconstruction "
                "pretrain (in-domain transfer), frozen for phase 2",
                "head": "single linear layer, fine-tuned with cross-entropy",
                "epochs": {"pretrain": PRETRAIN_EPOCHS, "head": HEAD_EPOCHS},
                "stop_criterion": "fixed epoch budget (no early stopping)",
            },
            "notes": (
                "Synthetic shape-separable windows make this task easy by "
                "construction; near-perfect accuracy reflects the data, not "
                "model quality. Real accuracy would require real labeled "
                "incident windows (out of demo scope)."
            ),
        }
    )

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": model.state_dict(),
            "classes": list(CLASS_ORDER),
            "confidence_threshold": threshold,
            "seed": args.seed,
        },
        ARTIFACTS_DIR / "predictor.pth",
    )
    (ARTIFACTS_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )
    print(f"test_accuracy={metrics['test_accuracy']} threshold={threshold}")
    print(f"artifacts written to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
