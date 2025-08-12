import os, json, logging, zipfile, io
import boto3
from urllib.parse import unquote_plus
from xml.etree import ElementTree as ET
from common import PROCESSED_BUCKET, write_s3_text, write_s3_json

log = logging.getLogger()
log.setLevel(logging.INFO)

sns = boto3.client('sns')
textract = boto3.client('textract')
s3 = boto3.client('s3')

def _extract_docx_text(file_bytes: bytes) -> str:
    """Extract text content from DOCX file using XML parsing."""
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
        xml_content = docx_zip.read('word/document.xml')
    
    root = ET.fromstring(xml_content)
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    paragraphs = []
    for paragraph in root.findall('.//w:p', namespace):
        text_runs = [run.text for run in paragraph.findall('.//w:t', namespace) if run.text]
        if text_runs:
            paragraphs.append(''.join(text_runs))
    
    return '\n'.join(paragraphs)

def _parse_document_path(s3_key: str) -> tuple[str, str]:
    """Parse S3 key to extract ingest date and document ID."""
    ingest_date = s3_key.split('ingest_date=')[-1].split('/')[0] if 'ingest_date=' in s3_key else '2025-08-12'
    doc_id = s3_key.split('/')[-1].rsplit('.', 1)[0]
    return ingest_date, doc_id

def _process_pdf_document(bucket: str, key: str, topic_arn: str, publish_role: str) -> None:
    """Start Textract analysis for PDF documents."""
    try:
        response = textract.start_document_analysis(
            DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
            FeatureTypes=['TABLES', 'FORMS'],
            NotificationChannel={'SNSTopicArn': topic_arn, 'RoleArn': publish_role},
            JobTag=key
        )
        log.info(f"Started Textract job {response['JobId']} for document {key}")
    except Exception as e:
        log.error(f"Failed to start Textract analysis for {key}: {str(e)}")
        raise

def _process_docx_document(bucket: str, key: str, ingest_date: str, doc_id: str) -> None:
    """Process DOCX document and extract text directly."""
    try:
        # Download and extract text
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read()
        extracted_text = _extract_docx_text(file_content)
        
        # Prepare metrics
        metrics = {
            'source_key': key,
            'doc_id': doc_id,
            'ingest_date': ingest_date,
            'pages': 1,
            'avg_confidence': 1.0,
            'min_confidence': 1.0,
            'text_length': len(extracted_text),
            'format': 'DOCX'
        }
        
        # Define output paths
        text_key = f"docs/text/{ingest_date}/{doc_id}.txt"
        json_key = f"docs/json/{ingest_date}/{doc_id}.json"
        metrics_key = f"docs/metrics/{ingest_date}/metrics.jsonl"
        
        # Write outputs
        write_s3_text(PROCESSED_BUCKET, text_key, extracted_text)
        write_s3_json(PROCESSED_BUCKET, json_key, metrics | {"text_s3": text_key})
        s3.put_object(Bucket=PROCESSED_BUCKET, Key=metrics_key, Body=(json.dumps(metrics) + "\n").encode('utf-8'))
        
        log.info(f"Successfully processed DOCX document {key}")
        
    except Exception as e:
        log.error(f"Failed to process DOCX document {key}: {str(e)}")
        raise

def handler(event, context):
    """Main handler for document processing router."""
    topic_arn = os.environ['SNS_TOPIC_ARN']
    publish_role = os.environ['TEXTRACT_PUBLISH_ROLE_ARN']

    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        s3_key = unquote_plus(record['s3']['object']['key'])
        
        # Only process documents in the docs/ prefix
        if not s3_key.lower().startswith('docs/'):
            continue

        # Parse document metadata
        ingest_date, doc_id = _parse_document_path(s3_key)
        file_extension = s3_key.lower().rsplit('.', 1)[-1]
        
        try:
            if file_extension == 'pdf':
                _process_pdf_document(bucket, s3_key, topic_arn, publish_role)
            elif file_extension == 'docx':
                _process_docx_document(bucket, s3_key, ingest_date, doc_id)
            else:
                log.warning(f"Unsupported file type: {file_extension} for document {s3_key}")
                
        except Exception as e:
            log.error(f"Failed to process document {s3_key}: {str(e)}")
            # Continue processing other documents

    return {"statusCode": 200, "body": "Document processing completed"}
