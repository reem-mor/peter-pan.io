"""Trained PyTorch classifier serving path (pytorch-predictor skill).

Architecture: a small 1D-CNN encoder pretrained self-supervised (window
reconstruction) on the unlabeled synthetic windows — the time-series crosswalk
of a pretrained image backbone (declared deviation #2: metric windows instead
of images) — then frozen, with only the linear classification head fine-tuned
on the six-class task. ``train.py`` produces
``predictor_service/artifacts/predictor.pth`` + ``metrics.json``; this module
loads the checkpoint once and serves it on CPU in eval mode.

Fixture-first rule: a missing artifact, a missing torch install, or
``PETER_PREDICTOR_ENGINE=stub`` all degrade gracefully to the fixed-weight
stub in ``classifier.py`` — the demo path never depends on the trained model.

Below-threshold behaviour (locked decision): the six-class ``incident_class``
enum is frozen — there is no seventh ``uncertain`` class. A softmax maximum
below ``confidence_threshold`` keeps the argmax class but marks the result
``below_threshold``; the route layer surfaces it as the ``uncertain`` fallback
so n8n can send it to human review instead of routing on a forced class.
"""

from __future__ import annotations

import logging
import math
import os
import pickle
import zipfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Canonical class order used by train.py; the checkpoint stores its own copy
# and inference always uses the checkpoint's order (single source at runtime).
CLASS_ORDER: tuple[str, ...] = (
    "cpu_saturation",
    "memory_leak",
    "db_lock_contention",
    "replication_lag",
    "error_rate_spike",
    "normal",
)

# Fixed input length the encoder was trained on; arbitrary-length service
# windows are linearly resampled to this before inference.
WINDOW_LEN = 64

# Softmax-max floor (start 0.6 per the pytorch-predictor skill; the trained
# checkpoint carries the value tuned on the validation set, which wins).
DEFAULT_CONFIDENCE_THRESHOLD = 0.6

_EMBEDDING_DIM = 128

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "predictor.pth"


def _build_model(n_classes: int):
    """Encoder (backbone) + linear head. Defined lazily so importing this
    module never requires torch (graceful degradation to the stub)."""
    import torch.nn as nn

    class WindowEncoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv1 = nn.Conv1d(1, 16, kernel_size=5, padding=2)
            self.conv2 = nn.Conv1d(16, 32, kernel_size=5, padding=2)
            self.pool = nn.MaxPool1d(2)
            self.out_pool = nn.AdaptiveAvgPool1d(4)
            self.act = nn.ReLU()

        def forward(self, x):  # (B, 1, WINDOW_LEN) -> (B, _EMBEDDING_DIM)
            x = self.pool(self.act(self.conv1(x)))
            x = self.act(self.conv2(x))
            x = self.out_pool(x)
            return x.flatten(1)

    class WindowClassifier(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.encoder = WindowEncoder()
            self.head = nn.Sequential(
                nn.Linear(_EMBEDDING_DIM, 64),
                nn.ReLU(),
                nn.Linear(64, n_classes),
            )

        def forward(self, x):
            return self.head(self.encoder(x))

    return WindowClassifier()


def preprocess(window: list[float]):
    """Sanitize -> resample to WINDOW_LEN -> per-window z-normalize.

    Must stay byte-identical between training and serving; train.py imports it.
    """
    import torch

    values = [float(v) if math.isfinite(v) else 0.0 for v in window]
    if not values:
        values = [0.0]
    if len(values) == 1:
        values = values * 2
    tensor = torch.tensor(values, dtype=torch.float32).view(1, 1, -1)
    tensor = torch.nn.functional.interpolate(
        tensor, size=WINDOW_LEN, mode="linear", align_corners=True
    )
    std, mean = torch.std_mean(tensor)
    return (tensor - mean) / max(float(std), 1e-6)


class TorchClassifier:
    """Loaded checkpoint wrapper — eval mode, CPU, ``no_grad`` inference."""

    def __init__(self, model: Any, classes: list[str], threshold: float) -> None:
        self._model = model
        self._classes = classes
        self.threshold = threshold

    def predict(self, window: list[float]) -> dict[str, Any]:
        import torch

        with torch.no_grad():
            logits = self._model(preprocess(window))
            probs = torch.softmax(logits, dim=1)[0]
        confidence, index = torch.max(probs, dim=0)
        confidence = float(confidence)
        return {
            "incident_class": self._classes[int(index)],
            "confidence": confidence,
            "engine": "torch",
            "below_threshold": confidence < self.threshold,
        }


_loaded: dict[str, TorchClassifier | None] = {}


def load_classifier() -> TorchClassifier | None:
    """Cached checkpoint loader; ``None`` means "use the stub"."""
    if os.environ.get("PETER_PREDICTOR_ENGINE", "auto") == "stub":
        return None
    path = os.environ.get("PETER_PREDICTOR_MODEL_PATH") or str(DEFAULT_MODEL_PATH)
    if path not in _loaded:
        _loaded[path] = _load_checkpoint(path)
    return _loaded[path]


def _load_checkpoint(path: str) -> TorchClassifier | None:
    try:
        import torch
    except ImportError:
        logger.warning("torch not installed — predictor falls back to the stub")
        return None
    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        classes = list(checkpoint["classes"])
        model = _build_model(len(classes))
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
    except FileNotFoundError:
        logger.warning(
            "predictor checkpoint missing at %s — falling back to the stub", path
        )
        return None
    except (
        OSError,
        KeyError,
        RuntimeError,
        ValueError,
        pickle.UnpicklingError,
        zipfile.BadZipFile,
    ) as exc:
        logger.error("failed to load predictor checkpoint %s: %s", path, exc)
        return None
    threshold = float(
        checkpoint.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
    )
    return TorchClassifier(model, classes, threshold)
