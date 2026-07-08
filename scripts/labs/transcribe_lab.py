#!/usr/bin/env python3
"""Course lab: Amazon Transcribe — list jobs and describe API access (no audio upload)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from botocore.exceptions import ClientError  # noqa: E402

from _common import client_error_hint, fail, ok, parse_lab_args, print_identity, session  # noqa: E402


def main() -> int:
    args = parse_lab_args("Amazon Transcribe lab — verify API access")
    sess = session(args.profile, args.region)
    print_identity(sess)
    transcribe = sess.client("transcribe")
    try:
        resp = transcribe.list_transcription_jobs(MaxResults=5, Status="COMPLETED")
        jobs = resp.get("TranscriptionJobSummaries", [])
        print(f"Recent completed jobs: {len(jobs)}")
        for job in jobs[:3]:
            print(f"  - {job.get('TranscriptionJobName')} ({job.get('LanguageCode')})")
        return ok(
            "Transcribe API reachable. Upload audio to S3 and call start_transcription_job "
            "for a full hands-on exercise."
        )
    except ClientError as exc:
        return fail(client_error_hint(exc))


if __name__ == "__main__":
    raise SystemExit(main())
