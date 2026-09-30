#!/usr/bin/env python3
"""Publish the dataset to Kaggle as a distribution copy.

Kaggle is a distribution channel, not the canonical record. The description in
kaggle/dataset-metadata.json points at stepuplaw.com and the GitHub repository.

    python3 scripts/push_kaggle.py            # first publication
    python3 scripts/push_kaggle.py --update --notes "..."   # new version

Needs the Kaggle token at ~/.kaggle/access_token.
"""
import argparse, os, pathlib, shutil, sys, tempfile, warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
os.environ.setdefault("KAGGLE_API_TOKEN",
                      open(os.path.expanduser("~/.kaggle/access_token")).read().strip())
from kaggle.api.kaggle_api_extended import KaggleApi

FILES = [
    ROOT / "kaggle" / "dataset-metadata.json",
    ROOT / "data" / "trusts_by_county.csv",
    ROOT / "data" / "trusts_statewide.json",
    ROOT / "data" / "schema.json",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--notes", default="New version")
    a = ap.parse_args()
    api = KaggleApi()
    api.authenticate()
    print(f"# authenticated as {api.get_config_value('username')}", file=sys.stderr)
    with tempfile.TemporaryDirectory() as stage:
        for f in FILES:
            shutil.copy2(f, os.path.join(stage, f.name))
        if a.update:
            api.dataset_create_version(stage, version_notes=a.notes, dir_mode="skip")
        else:
            api.dataset_create_new(stage, dir_mode="skip", public=True, quiet=False)
    print("https://www.kaggle.com/datasets/stepuplaw/florida-homes-in-trust-2026")


if __name__ == "__main__":
    main()
