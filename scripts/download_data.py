import shutil
from pathlib import Path

import polars as pl
from huggingface_hub import hf_hub_download

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

SAMPLE_SIZE = 10_000

REPO_ID = "McAuley-Lab/Amazon-Reviews-2023"
REVISION = "749931181c9cdd70bfa6408d8fe8b4ddd6107248"
FILENAME = "raw_review_All_Beauty/full-00000-of-00001.parquet"

RAW_PARQUET = RAW_DIR / "all_beauty_reviews.parquet"
SAMPLE_FILE = RAW_DIR / "sample_reviews.jsonl"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading All_Beauty reviews from Hugging Face...")
    print(f"Dataset revision: {REVISION}")

    dataset_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        revision=REVISION,
        repo_type="dataset",
    )

    print(f"Dataset available at: {dataset_path}")

    # Copy the downloaded raw dataset into our project.
    if not RAW_PARQUET.exists():
        print("Copying full dataset into data/raw...")
        shutil.copy2(dataset_path, RAW_PARQUET)
    else:
        print("Full dataset already exists in data/raw.")

    print(f"Raw dataset: {RAW_PARQUET}")

    print("Reading dataset with Polars...")

    df = pl.read_parquet(RAW_PARQUET)

    print(f"Total reviews: {len(df):,}")
    print(f"Columns: {df.columns}")

    sample = df.head(SAMPLE_SIZE)
    sample.write_ndjson(SAMPLE_FILE)

    print(f"Sample saved to: {SAMPLE_FILE}")
    print(f"Sample rows: {len(sample):,}")


if __name__ == "__main__":
    main()