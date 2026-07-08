#!/usr/bin/env python3
"""Course lab: Amazon Rekognition — list collections (read-only)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from botocore.exceptions import ClientError  # noqa: E402

from _common import client_error_hint, fail, ok, parse_lab_args, print_identity, session  # noqa: E402


def main() -> int:
    args = parse_lab_args("Amazon Rekognition lab — list collections")
    sess = session(args.profile, args.region)
    print_identity(sess)
    rekognition = sess.client("rekognition")
    try:
        resp = rekognition.list_collections(MaxResults=10)
        ids = resp.get("CollectionIds", [])
        print(f"Collections: {len(ids)}")
        for cid in ids[:5]:
            print(f"  - {cid}")
        return ok("Rekognition API reachable. Create a collection for face/image search labs.")
    except ClientError as exc:
        return fail(client_error_hint(exc))


if __name__ == "__main__":
    raise SystemExit(main())
