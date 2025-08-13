import sys
import re
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, upper, trim, regexp_replace, when, to_date, coalesce, lower
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import StringType

# Configure logging without external dependencies
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Get AWS region from environment or use default
aws_region = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "eu-west-2"))

# Arguments (injected by Glue job)
args = {k.replace("--", ""): v for k, v in zip(sys.argv[1::2], sys.argv[2::2]) if k.startswith("--")}
raw_bucket = args.get("raw_bucket")
processed_bucket = args.get("processed_bucket")
raw_prefix = args.get("raw_prefix", "contract_register/")
processed_prefix = args.get("processed_prefix", "contract_register/")

# Validate required arguments
if not raw_bucket or not processed_bucket:
    logger.error("Missing required arguments: raw_bucket and processed_bucket")
    sys.exit(1)

logger.info(f"Raw bucket: {raw_bucket}")
logger.info(f"Processed bucket: {processed_bucket}")
logger.info(f"Raw prefix: {raw_prefix}")
logger.info(f"Processed prefix: {processed_prefix}")
logger.info(f"AWS Region: {aws_region}")

def run_etl_with_pandas():
    """Fallback ETL using pandas when PySpark is not available."""
    try:
        import pandas as pd
        logger.info("Running ETL with pandas fallback...")
        
        # For local development, use sample data
        sample_data = {
            'contract_id': ['CTR001', 'CTR002', 'CTR003'],
            'party_a': ['Company A', 'Company B', 'Company C'],
            'party_b': ['Vendor X', 'Vendor Y', 'Vendor Z'],
            'effective_date': ['2024-01-01', '2024-01-15', '2024-02-01'],
            'end_date': ['2024-12-31', '2024-12-31', '2024-12-31'],
            'governing_law': ['US Law', 'UK Law', 'EU Law'],
            'amount': [100000, 250000, 500000],
            'currency': ['USD', 'GBP', 'EUR'],
            'dpa_present': ['Y', 'N', 'Y'],
            'contact_email': ['legal@companya.com', 'legal@companyb.com', 'legal@companyc.com'],
            'status': ['Active', 'Active', 'Active'],
            'review_due_date': ['2024-06-01', '2024-06-15', '2024-07-01']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Clean data
        df['party_a'] = df['party_a'].str.strip()
        df['party_b'] = df['party_b'].str.strip()
        df['currency'] = df['currency'].str.upper().str.strip()
        df['contact_email'] = df['contact_email'].str.strip().str.lower().str.replace(' ', '')
        
        # Date parsing
        for date_col in ['effective_date', 'end_date', 'review_due_date']:
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Currency validation
        valid_ccy = ["GBP", "EUR", "USD", "NGN", "ZAR", "INR"]
        df['currency'] = df['currency'].apply(lambda x: x if x in valid_ccy else "UNKNOWN")
        
        # DPA flag normalization
        df['dpa_present'] = df['dpa_present'].str.upper().str.strip()
        df['dpa_present'] = df['dpa_present'].apply(lambda x: x if x in ['Y', 'N'] else 'N')
        
        # Date logic fixes
        df.loc[df['end_date'] < df['effective_date'], 'end_date'] = None
        
        # Deduplicate
        df = df.drop_duplicates(subset=['contract_id'])
        
        # Save processed data
        output_path = "src/data/processed/contracts_processed.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"Processed {len(df)} rows with pandas")
        logger.info(f"Data saved to: {output_path}")
        return True
        
    except ImportError:
        logger.error("Pandas not available for fallback ETL")
        return False

try:
    spark = SparkSession.builder.appName("contract-register-etl").getOrCreate()

    raw_path = f"s3://{raw_bucket}/{raw_prefix}"
    processed_path = f"s3://{processed_bucket}/{processed_prefix}"

    logger.info(f"Raw path: {raw_path}")
    logger.info(f"Processed path: {processed_path}")

    # Configure Spark to use the correct region
    spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"s3.{aws_region}.amazonaws.com")
    spark.conf.set("spark.hadoop.fs.s3a.region", aws_region)

    # Read CSVs (allow messy headers)
    logger.info("Reading CSV data from S3...")
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_path)

    if df.count() == 0:
        logger.warning("No data found in source path")
        sys.exit(0)

    logger.info(f"Read {df.count()} rows from source")

    # Normalise column names
    for c in df.columns:
        df = df.withColumnRenamed(c, re.sub(r"[^a-z0-9_]+", "_", c.strip().lower()))

    # Required columns (if missing, create as null)
    required = [
        "contract_id",
        "party_a",
        "party_b",
        "effective_date",
        "end_date",
        "governing_law",
        "amount",
        "currency",
        "dpa_present",
        "contact_email",
        "status",
        "review_due_date",
    ]
    for r in required:
        if r not in df.columns:
            df = df.withColumn(r, lit(None).cast(StringType()))

    # Trim & uppercase currency
    clean = (
        df.withColumn("party_a", trim(col("party_a")))
        .withColumn("party_b", trim(col("party_b")))
        .withColumn("currency", upper(trim(col("currency"))))
        .withColumn("contact_email", trim(col("contact_email")))
    )

    # Basic email cleanup (lowercase, remove spaces)
    clean = clean.withColumn("contact_email", regexp_replace(lower(col("contact_email")), " ", ""))

    # Date parsing (YYYY-MM-DD expected; adjust if needed)
    for d in ["effective_date", "end_date", "review_due_date"]:
        clean = clean.withColumn(d, to_date(col(d)))

    # Currency whitelist
    valid_ccy = ["GBP", "EUR", "USD", "NGN", "ZAR", "INR"]
    clean = clean.withColumn(
        "currency", when(col("currency").isin(valid_ccy), col("currency")).otherwise(lit("UNKNOWN"))
    )

    # DPA flag normalisation
    clean = clean.withColumn("dpa_present", upper(trim(col("dpa_present"))))
    clean = clean.withColumn(
        "dpa_present", when(col("dpa_present").isin("Y", "N"), col("dpa_present")).otherwise(lit("N"))
    )

    # Date logic fixes: if end_date before effective_date, swap to null end_date
    clean = clean.withColumn("end_date", when(col("end_date") < col("effective_date"), None).otherwise(col("end_date")))

    # Deduplicate on (contract_id) then fallback key
    if "contract_id" in clean.columns:
        windowed = clean.dropDuplicates(["contract_id"])
    else:
        windowed = clean.dropDuplicates(["party_a", "party_b", "effective_date"])

    logger.info(f"Writing {windowed.count()} processed rows to S3...")

    # Write Parquet (overwrite partition-free for simplicity in dev)
    (windowed.coalesce(1).write.mode("overwrite").parquet(processed_path))

    logger.info("ETL job completed successfully")

except ImportError as e:
    if "pyspark" in str(e).lower():
        logger.warning("PySpark not available, using pandas fallback...")
        if not run_etl_with_pandas():
            logger.error("ETL job failed - no suitable processing engine available")
            sys.exit(1)
    else:
        logger.error(f"Import error: {e}")
        sys.exit(1)
except Exception as e:
    logger.error(f"ETL job failed: {str(e)}")
    sys.exit(1)
finally:
    if "spark" in locals():
        spark.stop()
