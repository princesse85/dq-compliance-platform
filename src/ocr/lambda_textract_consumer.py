import os, json, logging
import boto3
from common import PROCESSED_BUCKET, write_s3_text, write_s3_json

log = logging.getLogger()
log.setLevel(logging.INFO)

textract = boto3.client('textract')
s3 = boto3.client('s3')

def _extract_text_from_blocks(blocks):
    """Extract text and confidence scores from Textract blocks."""
    lines = []
    confidences = []
    for block in blocks:
        if block.get('BlockType') == 'LINE':
            text = block.get('Text', '')
            confidence = block.get('Confidence', 0.0)
            if text:
                lines.append(text)
                confidences.append(confidence)
    return '\n'.join(lines), confidences

def handler(event, context):
    """Process Textract completion notifications and extract document text."""
    for record in event.get('Records', []):
        body = json.loads(record['body'])
        message = json.loads(body['Message']) if 'Message' in body else body
        
        job_id = message.get('JobId')
        status = message.get('Status')
        job_tag = message.get('JobTag', '')
        
        if status != 'SUCCEEDED':
            log.warning(f"Textract job {job_id} failed with status: {status}")
            continue

        # Fetch all pages from Textract
        blocks = []
        pages = 0
        next_token = None
        
        while True:
            if next_token:
                response = textract.get_document_analysis(JobId=job_id, NextToken=next_token)
            else:
                response = textract.get_document_analysis(JobId=job_id)
            
            blocks.extend(response.get('Blocks', []))
            pages = max(pages, response.get('DocumentMetadata', {}).get('Pages', pages))
            next_token = response.get('NextToken')
            
            if not next_token:
                break

        # Extract text and calculate metrics
        text, confidences = _extract_text_from_blocks(blocks)
        avg_confidence = round(sum(confidences)/len(confidences), 4) if confidences else 0.0
        min_confidence = round(min(confidences), 4) if confidences else 0.0

        # Parse document metadata
        ingest_date = job_tag.split('ingest_date=')[-1].split('/')[0] if 'ingest_date=' in job_tag else '2025-08-12'
        doc_id = job_tag.split('/')[-1].rsplit('.', 1)[0]

        # Define output paths
        text_key = f"docs/text/{ingest_date}/{doc_id}.txt"
        json_key = f"docs/json/{ingest_date}/{doc_id}.json"
        metrics_key = f"docs/metrics/{ingest_date}/metrics.jsonl"

        # Prepare metrics
        metrics = {
            'source_key': job_tag,
            'doc_id': doc_id,
            'ingest_date': ingest_date,
            'pages': pages,
            'avg_confidence': avg_confidence,
            'min_confidence': min_confidence,
            'text_length': len(text),
            'format': 'PDF'
        }

        # Write outputs
        write_s3_text(PROCESSED_BUCKET, text_key, text)
        write_s3_json(PROCESSED_BUCKET, json_key, metrics | {"text_s3": text_key})
        s3.put_object(Bucket=PROCESSED_BUCKET, Key=metrics_key, Body=(json.dumps(metrics) + "\n").encode('utf-8'))

    return {"statusCode": 200, "body": "Processing completed"}
