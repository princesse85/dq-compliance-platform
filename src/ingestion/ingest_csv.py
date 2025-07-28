import os
import sys
import boto3
import pandas as pd
from datetime import datetime
from pathlib import Path

AWS_BUCKET = os.getenv("DQ_BUCKET")
if not AWS_BUCKET:
    sys.exit("Set DQ_BUCKET env-var pointing to your landing-zone S3 bucket")

def upload_csv(local_path: Path):
    """Read a local CSV, do minimal validation, push to S3."""
    df = pd.read_csv(local_path)
    if df.isnull().any().any():
        print("⚠️  Nulls detected – continuing (DQ handled later)")
    s3_key = f"raw/{datetime.now():%Y%m%d}/{local_path.name}"
    boto3.client("s3").upload_file(str(local_path), AWS_BUCKET, s3_key)
    print(f"✔ Uploaded to s3://{AWS_BUCKET}/{s3_key}")

if __name__ == "__main__":
    upload_csv(Path("../../data/raw/sample_address_book.csv").resolve())
