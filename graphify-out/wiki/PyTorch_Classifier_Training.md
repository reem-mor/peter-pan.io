# PyTorch Classifier Training

> 33 nodes · cohesion 0.12

## Key Concepts

- **train.py** (13 connections) — `services/predictor/train.py`
- **main()** (10 connections) — `services/predictor/train.py`
- **torch_classifier.py** (8 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **Random** (7 connections)
- **load_classifier()** (6 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **TorchClassifier** (6 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **pretrain_encoder()** (5 connections) — `services/predictor/train.py`
- **threshold_report()** (5 connections) — `services/predictor/train.py`
- **train_head()** (5 connections) — `services/predictor/train.py`
- **Tensor** (5 connections)
- **Module** (4 connections)
- **_build_model()** (4 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **_load_checkpoint()** (4 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **preprocess()** (4 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **_batch()** (4 connections) — `services/predictor/train.py`
- **build_dataset()** (4 connections) — `services/predictor/train.py`
- **evaluate()** (4 connections) — `services/predictor/train.py`
- **_make_window()** (4 connections) — `services/predictor/train.py`
- **stratified_split()** (4 connections) — `services/predictor/train.py`
- **.predict()** (3 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **_noise()** (3 connections) — `services/predictor/train.py`
- **Any** (2 connections)
- **.__init__()** (2 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **Trained PyTorch classifier serving path (pytorch-predictor skill).  Architectu** (1 connections) — `services/predictor/predictor_service/torch_classifier.py`
- **Loaded checkpoint wrapper — eval mode, CPU, ``no_grad`` inference.** (1 connections) — `services/predictor/predictor_service/torch_classifier.py`
- *... and 8 more nodes in this community*

## Relationships

- [Predictor Service API](Predictor_Service_API.md) (3 shared connections)
- [Alert Stream Generator](Alert_Stream_Generator.md) (1 shared connections)

## Source Files

- `services/predictor/predictor_service/torch_classifier.py`
- `services/predictor/train.py`

## Audit Trail

- EXTRACTED: 122 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*