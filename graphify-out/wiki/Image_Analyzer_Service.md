# Image Analyzer Service

> 28 nodes · cohesion 0.09

## Key Concepts

- **app.py** (7 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **analyze_image()** (6 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **ImageAnalyzerModel** (6 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **schemas.py** (5 connections) — `services/image-analyzer/image_analyzer_service/schemas.py`
- **get_model()** (4 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **.load_image_from_url()** (4 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **AnalyzeImageRequest** (4 connections) — `services/image-analyzer/image_analyzer_service/schemas.py`
- **AnalyzeImageResponse** (4 connections) — `services/image-analyzer/image_analyzer_service/schemas.py`
- **RoomClassification** (4 connections) — `services/image-analyzer/image_analyzer_service/schemas.py`
- **models.py** (3 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **.analyze()** (3 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **BaseModel** (3 connections)
- **require_bearer_token()** (2 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **Image** (1 connections)
- **healthz()** (1 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **FastAPI app for the Image Analyzer microservice (Stage A: ResNet room classifica** (1 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **Lazy-load model on first request.** (1 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set.** (1 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **Analyze a property image for room type and condition.** (1 connections) — `services/image-analyzer/image_analyzer_service/app.py`
- **.__init__()** (1 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **Simple room classification model (Stage A fixture).** (1 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **Mock room classification model for Stage A.** (1 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **Load image from URL or base64 data URI.** (1 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **Analyze image and return room type + condition score (fixture).** (1 connections) — `services/image-analyzer/image_analyzer_service/models.py`
- **Pydantic models for image analyzer API contracts.** (1 connections) — `services/image-analyzer/image_analyzer_service/schemas.py`
- *... and 3 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `services/image-analyzer/image_analyzer_service/app.py`
- `services/image-analyzer/image_analyzer_service/models.py`
- `services/image-analyzer/image_analyzer_service/schemas.py`

## Audit Trail

- EXTRACTED: 68 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*