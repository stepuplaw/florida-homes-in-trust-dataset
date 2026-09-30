#!/usr/bin/env python3
"""Push the dataset to Hugging Face as the AI-facing mirror.

The canonical record stays at stepuplaw.com and the source of truth stays in
git. This is a mirror, and its card links home rather than competing.

Run `hf auth login` (or set HF_TOKEN) first, then

    python3 scripts/push_huggingface.py

Add --dry-run to see exactly what would be uploaded without touching anything.
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ID = "StepUpLaw/florida-homes-in-trust-2026"

# Card first: on Hugging Face the README IS the dataset page.
FILES = [
    (ROOT / "huggingface" / "README.md", "README.md"),
    (ROOT / "data" / "trusts_by_county.csv", "trusts_by_county.csv"),
    (ROOT / "data" / "trusts_statewide.json", "trusts_statewide.json"),
    (ROOT / "data" / "schema.json", "schema.json"),
    (ROOT / "LICENSE", "LICENSE"),
    (ROOT / "CITATION.cff", "CITATION.cff"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    missing = [str(src) for src, _ in FILES if not src.exists()]
    if missing:
        sys.exit("missing files:\n  " + "\n  ".join(missing))

    print(f"repo: {REPO_ID}")
    for src, dest in FILES:
        print(f"  {dest:24} {src.stat().st_size:>8,} bytes")
    if args.dry_run:
        print("\ndry run, nothing uploaded")
        return

    from huggingface_hub import HfApi
    api = HfApi()
    print(f"\nauthenticated as: {api.whoami().get('name')}")
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
    for src, dest in FILES:
        api.upload_file(path_or_fileobj=str(src), path_in_repo=dest,
                        repo_id=REPO_ID, repo_type="dataset")
        print(f"  uploaded {dest}")
    print(f"\nhttps://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
