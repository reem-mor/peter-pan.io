# AWS AI services — course labs

Minimal boto3 scripts for syllabus topics **not** covered by the PITER Bedrock app.

| Script | Service | What it does |
|--------|---------|--------------|
| `transcribe_lab.py` | Transcribe | Lists recent transcription jobs |
| `polly_lab.py` | Polly | Lists available voices |
| `textract_lab.py` | Textract | Lists custom adapters (API smoke test) |
| `rekognition_lab.py` | Rekognition | Lists face collections |
| `comprehend_lab.py` | Comprehend | `detect_dominant_language` on sample ops text |

## Usage

```powershell
cd C:\dev\peter-pan.io
$env:AWS_PROFILE = "reemmor"

.\.venv\Scripts\python.exe scripts\labs\run_all_labs.py
# or one lab:
.\.venv\Scripts\python.exe scripts\labs\comprehend_lab.py --profile reemmor --region us-east-1
```

Requires IAM permissions for each service in your profile. Failures usually mean missing `Allow` on that API — fix in IAM or use the AWS Console equivalent lab.

See also [`docs/course_coverage.md`](../../docs/course_coverage.md).
