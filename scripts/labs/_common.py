#!/usr/bin/env python3
"""Shared helpers for AWS AI service course labs (read-only / safe defaults)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402


def parse_lab_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--profile", default="", help="AWS profile (default: credential chain)")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    return parser.parse_args()


def session(profile: str, region: str) -> boto3.Session:
    kwargs: dict[str, str] = {"region_name": region}
    if profile.strip():
        kwargs["profile_name"] = profile.strip()
    return boto3.Session(**kwargs)


def print_identity(sess: boto3.Session) -> None:
    sts = sess.client("sts")
    ident = sts.get_caller_identity()
    print(f"Account: {ident.get('Account')}")
    print(f"ARN: {ident.get('Arn')}")


def ok(message: str) -> int:
    print(f"OK: {message}")
    return 0


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def client_error_hint(exc: ClientError) -> str:
    err = exc.response.get("Error", {})
    return f"{err.get('Code', 'ClientError')}: {err.get('Message', exc)}"
