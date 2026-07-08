#!/usr/bin/env python3
"""Course lab: Amazon Comprehend — detect dominant language on sample text."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from botocore.exceptions import ClientError  # noqa: E402

from _common import client_error_hint, fail, ok, parse_lab_args, print_identity, session  # noqa: E402

_SAMPLE = (
    "PITER AiOps incident triage: auth-service login failures in production "
    "require runbook RB-AUTH-001 and escalation to platform on-call."
)


def main() -> int:
    args = parse_lab_args("Amazon Comprehend lab — detect_dominant_language")
    sess = session(args.profile, args.region)
    print_identity(sess)
    comprehend = sess.client("comprehend")
    try:
        resp = comprehend.detect_dominant_language(Text=_SAMPLE)
        langs = resp.get("Languages", [])
        for lang in langs[:3]:
            print(f"  - {lang.get('LanguageCode')}: {lang.get('Score'):.2f}")
        return ok("Comprehend API reachable. Try detect_sentiment or detect_entities next.")
    except ClientError as exc:
        return fail(client_error_hint(exc))


if __name__ == "__main__":
    raise SystemExit(main())
