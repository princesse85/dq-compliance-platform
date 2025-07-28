#!/usr/bin/env bash
set -e
BUCKET=${DQ_BUCKET:-"<your-bucket-name>"}

aws s3 cp data/raw/sample_address_book.csv s3://$BUCKET/raw/$(date +%Y%m%d)/
echo "✔ Sample CSV uploaded to $BUCKET"
