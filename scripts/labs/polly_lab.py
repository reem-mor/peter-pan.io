#!/usr/bin/env python3
"""Course lab: Amazon Polly — list voices and optional synthesis to stdout metadata."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from botocore.exceptions import ClientError  # noqa: E402

from _common import client_error_hint, fail, ok, parse_lab_args, print_identity, session  # noqa: E402


def main() -> int:
    args = parse_lab_args("Amazon Polly lab — list voices")
    sess = session(args.profile, args.region)
    print_identity(sess)
    polly = sess.client("polly")
    try:
        voices = polly.describe_voices(LanguageCode="en-US").get("Voices", [])
        print(f"English (US) voices available: {len(voices)}")
        for voice in voices[:5]:
            print(f"  - {voice.get('Id')} ({voice.get('Gender')})")
        return ok("Polly API reachable. Use synthesize_speech for audio output.")
    except ClientError as exc:
        return fail(client_error_hint(exc))


if __name__ == "__main__":
    raise SystemExit(main())
