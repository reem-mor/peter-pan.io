#!/usr/bin/env python3
"""Course lab: Amazon Textract — verify API access via list_adapters (read-only)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from botocore.exceptions import ClientError  # noqa: E402

from _common import client_error_hint, fail, ok, parse_lab_args, print_identity, session  # noqa: E402


def main() -> int:
    args = parse_lab_args("Amazon Textract lab — list adapters")
    sess = session(args.profile, args.region)
    print_identity(sess)
    textract = sess.client("textract")
    try:
        resp = textract.list_adapters(MaxResults=5)
        adapters = resp.get("Adapters", [])
        print(f"Custom adapters: {len(adapters)}")
        for adapter in adapters[:3]:
            print(f"  - {adapter.get('AdapterId')} ({adapter.get('AdapterName')})")
        return ok("Textract API reachable. Use S3 analyze_document for PDF/image OCR labs.")
    except ClientError as exc:
        return fail(client_error_hint(exc))


if __name__ == "__main__":
    raise SystemExit(main())
