import os
import json
import pandas as pd
import boto3
from io import StringIO
from datetime import datetime
from dateutil.parser import isoparse
from expectations_contract_register import REQUIRED_COLS, VALID_CCY
from utils import is_email, parse_date
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

S3 = boto3.client('s3')

RAW_PREFIX = "contract_register/"
PRO_PREFIX = "contract_register/"

def s3_read_csv(bucket, key):
    obj = S3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(obj['Body'])

def s3_write_text(bucket, key, text):
    S3.put_object(Bucket=bucket, Key=key, Body=text.encode('utf-8'))


def composite_quality(df):
    total = len(df)
    if total == 0:
        return 0.0

    checks = {
        'required_fields': df[REQUIRED_COLS].notna().all(axis=1),
        'valid_currency': df['currency'].astype(str).str.upper().isin(VALID_CCY),
        'valid_email': df['contact_email'].astype(str).apply(is_email),
        'date_order': pd.to_datetime(df['end_date'], errors='coerce') >= pd.to_datetime(df['effective_date'], errors='coerce'),
        'no_future_dates': pd.to_datetime(df['effective_date'], errors='coerce') <= pd.Timestamp.now(tz=None),
        'dpa_flag': df['dpa_present'].astype(str).str.upper().isin(['Y','N'])
    }

    row_pass = pd.DataFrame(checks).all(axis=1)
    score = round(100 * row_pass.sum() / total, 2)

    failures = {name: int((~mask).sum()) for name, mask in checks.items()}
    return score, failures


def run(bucket_raw, bucket_analytics, ingest_date_folder):
    # Find latest raw CSV
    prefix = f"{RAW_PREFIX}{ingest_date_folder}/"
    listed = S3.list_objects_v2(Bucket=bucket_raw, Prefix=prefix)
    keys = [c['Key'] for c in listed.get('Contents', []) if c['Key'].lower().endswith('.csv')]
    if not keys:
        raise RuntimeError(f"No CSV found under s3://{bucket_raw}/{prefix}")

    key = sorted(keys)[-1]
    df = s3_read_csv(bucket_raw, key)

    baseline, base_fail = composite_quality(df)

    # Write baseline log
    ts = datetime.utcnow().isoformat()
    log = {
        'timestamp': ts,
        'dataset': 'contract_register_raw',
        'key': key,
        'baseline_score': baseline,
        'baseline_failures': base_fail,
    }
    s3_write_text(bucket_analytics, f"quality_logs/{ingest_date_folder}/baseline.json", json.dumps(log, indent=2))

    # After ETL, read processed parquet back via AWS Data Wrangler (optional) or rely on ETL result.
    # For simplicity, assume ETL has written a single parquet file under processed/contract_register/
    # Here we just reuse df to simulate post-fix if you run after ETL, switch to reading processed.

    # If you want real processed read as CSV (you can export Parquet to CSV later) or use awswrangler.

    post = baseline  # placeholder; can be replaced with processed read

    # Save placeholder post log; you can re-run after ETL and swap in processed read
    log['post_score'] = post
    s3_write_text(bucket_analytics, f"quality_logs/{ingest_date_folder}/post.json", json.dumps(log, indent=2))

    return baseline, post

if __name__ == "__main__":
    raw_bucket = os.environ.get('RAW_BUCKET')
    analytics_bucket = os.environ.get('ANALYTICS_BUCKET')
    ingest_date = os.environ.get('INGEST_DATE')  # e.g., 2025-08-11
    b, p = run(raw_bucket, analytics_bucket, ingest_date)
    logger.info(f"Quality metrics - baseline: {b}, post: {p}")
