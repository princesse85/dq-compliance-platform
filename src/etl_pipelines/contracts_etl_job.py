import sys
import re
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, upper, trim, regexp_replace, when, to_date, coalesce, lower
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import StringType

# Configure logging without external dependencies
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get AWS region from environment or use default
aws_region = os.getenv('AWS_DEFAULT_REGION', 'eu-west-2')

# Arguments (injected by Glue job)
args = {k.replace('--',''): v for k,v in zip(sys.argv[1::2], sys.argv[2::2]) if k.startswith('--')}
raw_bucket = args.get('raw_bucket')
processed_bucket = args.get('processed_bucket')
raw_prefix = args.get('raw_prefix', 'contract_register/')
processed_prefix = args.get('processed_prefix', 'contract_register/')

# Validate required arguments
if not raw_bucket or not processed_bucket:
    logger.error("Missing required arguments: raw_bucket and processed_bucket")
    sys.exit(1)

logger.info(f"Raw bucket: {raw_bucket}")
logger.info(f"Processed bucket: {processed_bucket}")
logger.info(f"Raw prefix: {raw_prefix}")
logger.info(f"Processed prefix: {processed_prefix}")
logger.info(f"AWS Region: {aws_region}")

try:
    spark = SparkSession.builder.appName('contract-register-etl').getOrCreate()

    raw_path = f"s3://{raw_bucket}/{raw_prefix}"
    processed_path = f"s3://{processed_bucket}/{processed_prefix}"

    logger.info(f"Raw path: {raw_path}")
    logger.info(f"Processed path: {processed_path}")

    # Configure Spark to use the correct region
    spark.conf.set("spark.hadoop.fs.s3a.endpoint", f"s3.{aws_region}.amazonaws.com")
    spark.conf.set("spark.hadoop.fs.s3a.region", aws_region)

    # Read CSVs (allow messy headers)
    logger.info("Reading CSV data from S3...")
    df = spark.read.option('header','true').option('inferSchema','true').csv(raw_path)
    
    if df.count() == 0:
        logger.warning("No data found in source path")
        sys.exit(0)

    logger.info(f"Read {df.count()} rows from source")

    # Normalise column names
    for c in df.columns:
        df = df.withColumnRenamed(c, re.sub(r'[^a-z0-9_]+','_', c.strip().lower()))

    # Required columns (if missing, create as null)
    required = ['contract_id','party_a','party_b','effective_date','end_date','governing_law','amount','currency','dpa_present','contact_email','status','review_due_date']
    for r in required:
        if r not in df.columns:
            df = df.withColumn(r, lit(None).cast(StringType()))

    # Trim & uppercase currency
    clean = (df
        .withColumn('party_a', trim(col('party_a')))
        .withColumn('party_b', trim(col('party_b')))
        .withColumn('currency', upper(trim(col('currency'))))
        .withColumn('contact_email', trim(col('contact_email')))
    )

    # Basic email cleanup (lowercase, remove spaces)
    clean = clean.withColumn('contact_email', regexp_replace(lower(col('contact_email')), ' ', ''))

    # Date parsing (YYYY-MM-DD expected; adjust if needed)
    for d in ['effective_date','end_date','review_due_date']:
        clean = clean.withColumn(d, to_date(col(d)))

    # Currency whitelist
    valid_ccy = ["GBP","EUR","USD","NGN","ZAR","INR"]
    clean = clean.withColumn('currency', when(col('currency').isin(valid_ccy), col('currency')).otherwise(lit('UNKNOWN')))

    # DPA flag normalisation
    clean = clean.withColumn('dpa_present', upper(trim(col('dpa_present'))))
    clean = clean.withColumn('dpa_present', when(col('dpa_present').isin('Y','N'), col('dpa_present')).otherwise(lit('N')))

    # Date logic fixes: if end_date before effective_date, swap to null end_date
    clean = clean.withColumn('end_date', when(col('end_date') < col('effective_date'), None).otherwise(col('end_date')))

    # Deduplicate on (contract_id) then fallback key
    if 'contract_id' in clean.columns:
        windowed = clean.dropDuplicates(['contract_id'])
    else:
        windowed = clean.dropDuplicates(['party_a','party_b','effective_date'])

    logger.info(f"Writing {windowed.count()} processed rows to S3...")

    # Write Parquet (overwrite partition-free for simplicity in dev)
    (windowed
        .coalesce(1)
        .write.mode('overwrite').parquet(processed_path)
    )

    logger.info("ETL job completed successfully")

except Exception as e:
    logger.error(f"ETL job failed: {str(e)}")
    sys.exit(1)
finally:
    if 'spark' in locals():
        spark.stop()
