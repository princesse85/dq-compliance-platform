import pytest
import boto3
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
from moto import mock_aws

from src.data_quality.quality_assessment import DataQualityAssessment
from src.etl_pipelines.contracts_etl_job import ContractsETLJob


class TestAWSS3Integration:
    """Integration tests for AWS S3 operations"""
    
    @mock_aws
    def setup_method(self):
        """Setup S3 mock and test data"""
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = 'test-data-quality-bucket'
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        
        self.test_data = pd.DataFrame({
            'contract_id': ['C001', 'C002', 'C003'],
            'client_name': ['Client A', 'Client B', 'Client C'],
            'contract_value': [100000, 250000, 75000],
            'status': ['Active', 'Active', 'Pending']
        })
    
    def test_s3_data_upload_and_download(self):
        """Test S3 data upload and download operations"""
        # Upload data to S3
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            self.test_data.to_csv(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name
        
        try:
            # Upload to S3
            s3_key = 'raw-data/contracts.csv'
            self.s3_client.upload_file(tmp_file_path, self.bucket_name, s3_key)
            
            # Verify upload
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            assert response['ContentLength'] > 0
            
            # Download from S3
            download_path = tmp_file_path.replace('.csv', '_downloaded.csv')
            self.s3_client.download_file(self.bucket_name, s3_key, download_path)
            
            # Verify download
            downloaded_data = pd.read_csv(download_path)
            assert len(downloaded_data) == len(self.test_data)
            assert list(downloaded_data.columns) == list(self.test_data.columns)
            
        finally:
            # Cleanup
            os.unlink(tmp_file_path)
            if os.path.exists(download_path):
                os.unlink(download_path)
    
    def test_s3_data_processing_pipeline(self):
        """Test S3 data processing pipeline"""
        # Upload raw data
        raw_data_key = 'raw-data/contracts.csv'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            self.test_data.to_csv(tmp_file.name, index=False)
            self.s3_client.upload_file(tmp_file.name, self.bucket_name, raw_data_key)
            os.unlink(tmp_file.name)
        
        # Process data (simulate ETL)
        etl_job = ContractsETLJob()
        processed_data = etl_job.transform_data(self.test_data)
        
        # Upload processed data
        processed_data_key = 'processed-data/contracts_enriched.csv'
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            processed_data.to_csv(tmp_file.name, index=False)
            self.s3_client.upload_file(tmp_file.name, self.bucket_name, processed_data_key)
            os.unlink(tmp_file.name)
        
        # Verify both files exist
        raw_response = self.s3_client.head_object(Bucket=self.bucket_name, Key=raw_data_key)
        processed_response = self.s3_client.head_object(Bucket=self.bucket_name, Key=processed_data_key)
        
        assert raw_response['ContentLength'] > 0
        assert processed_response['ContentLength'] > 0
    
    def test_s3_data_quality_assessment(self):
        """Test S3 data quality assessment workflow"""
        # Upload data with quality issues
        problematic_data = self.test_data.copy()
        problematic_data.loc[0, 'contract_value'] = -1000  # Invalid value
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            problematic_data.to_csv(tmp_file.name, index=False)
            self.s3_client.upload_file(tmp_file.name, self.bucket_name, 'quality-test/contracts.csv')
            os.unlink(tmp_file.name)
        
        # Download and assess quality
        download_path = '/tmp/quality_test_contracts.csv'
        self.s3_client.download_file(self.bucket_name, 'quality-test/contracts.csv', download_path)
        
        downloaded_data = pd.read_csv(download_path)
        quality_assessment = DataQualityAssessment()
        quality_report = quality_assessment.assess_quality(downloaded_data)
        
        # Verify quality assessment
        assert quality_report['overall_score'] < 1.0
        assert 'validation_errors' in quality_report
        
        # Cleanup
        os.unlink(download_path)


class TestAWSLambdaIntegration:
    """Integration tests for AWS Lambda functions"""
    
    @mock_aws
    def setup_method(self):
        """Setup Lambda mock"""
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.function_name = 'test-data-quality-function'
    
    def test_lambda_function_creation_and_invocation(self):
        """Test Lambda function creation and invocation"""
        # Create test Lambda function
        function_code = '''
import json
import pandas as pd

def lambda_handler(event, context):
    # Simulate data quality assessment
    data = event.get('data', [])
    df = pd.DataFrame(data)
    
    # Calculate basic quality metrics
    completeness = 1 - df.isnull().sum().sum() / (len(df) * len(df.columns))
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'completeness_score': float(completeness),
            'record_count': len(df),
            'column_count': len(df.columns)
        })
    }
'''
        
        # Create function
        self.lambda_client.create_function(
            FunctionName=self.function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::123456789012:role/lambda-role',
            Handler='index.lambda_handler',
            Code={'ZipFile': function_code.encode()}
        )
        
        # Test invocation
        test_data = [
            {'contract_id': 'C001', 'value': 100000},
            {'contract_id': 'C002', 'value': 250000},
            {'contract_id': 'C003', 'value': 75000}
        ]
        
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            Payload=json.dumps({'data': test_data})
        )
        
        # Verify response
        response_payload = json.loads(response['Payload'].read())
        assert response_payload['statusCode'] == 200
        
        body = json.loads(response_payload['body'])
        assert body['completeness_score'] == 1.0
        assert body['record_count'] == 3
        assert body['column_count'] == 2


class TestAWSSQSIntegration:
    """Integration tests for AWS SQS message processing"""
    
    @mock_aws
    def setup_method(self):
        """Setup SQS mock"""
        self.sqs_client = boto3.client('sqs', region_name='us-east-1')
        self.queue_name = 'test-data-quality-queue'
        
        # Create queue
        response = self.sqs_client.create_queue(QueueName=self.queue_name)
        self.queue_url = response['QueueUrl']
    
    def test_sqs_message_processing_pipeline(self):
        """Test SQS message processing pipeline"""
        # Send test messages
        test_messages = [
            {
                'contract_id': 'C001',
                'client_name': 'Client A',
                'contract_value': 100000,
                'status': 'Active'
            },
            {
                'contract_id': 'C002',
                'client_name': 'Client B',
                'contract_value': 250000,
                'status': 'Active'
            }
        ]
        
        for message in test_messages:
            self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message)
            )
        
        # Receive and process messages
        response = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10
        )
        
        messages = response.get('Messages', [])
        assert len(messages) == 2
        
        # Process each message
        processed_messages = []
        for message in messages:
            message_body = json.loads(message['Body'])
            
            # Simulate data quality check
            quality_score = 1.0 if message_body['contract_value'] > 0 else 0.0
            message_body['quality_score'] = quality_score
            
            processed_messages.append(message_body)
            
            # Delete processed message
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
        
        # Verify processing
        assert len(processed_messages) == 2
        assert all(msg['quality_score'] == 1.0 for msg in processed_messages)


class TestAWSSNSIntegration:
    """Integration tests for AWS SNS notifications"""
    
    @mock_aws
    def setup_method(self):
        """Setup SNS mock"""
        self.sns_client = boto3.client('sns', region_name='us-east-1')
        self.topic_name = 'test-data-quality-alerts'
        
        # Create topic
        response = self.sns_client.create_topic(Name=self.topic_name)
        self.topic_arn = response['TopicArn']
    
    def test_sns_quality_alert_notifications(self):
        """Test SNS quality alert notifications"""
        # Subscribe email to topic
        email = 'test@example.com'
        self.sns_client.subscribe(
            TopicArn=self.topic_arn,
            Protocol='email',
            Endpoint=email
        )
        
        # Send quality alert
        alert_message = {
            'alert_type': 'data_quality_issue',
            'severity': 'high',
            'description': 'Contract value contains negative numbers',
            'affected_records': 5,
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        response = self.sns_client.publish(
            TopicArn=self.topic_arn,
            Message=json.dumps(alert_message),
            Subject='Data Quality Alert'
        )
        
        # Verify message was sent
        assert 'MessageId' in response
        
        # Test multiple alerts
        alerts = [
            {'type': 'completeness', 'severity': 'medium'},
            {'type': 'accuracy', 'severity': 'high'},
            {'type': 'consistency', 'severity': 'low'}
        ]
        
        for alert in alerts:
            self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(alert),
                Subject=f'Data Quality Alert: {alert["type"]}'
            )


class TestAWSCloudWatchIntegration:
    """Integration tests for AWS CloudWatch monitoring"""
    
    @mock_aws
    def setup_method(self):
        """Setup CloudWatch mock"""
        self.cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
    
    def test_cloudwatch_metrics_publishing(self):
        """Test CloudWatch metrics publishing"""
        # Publish data quality metrics
        metrics = [
            {
                'MetricName': 'DataQualityScore',
                'Value': 0.95,
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'Dataset', 'Value': 'contracts'},
                    {'Name': 'Environment', 'Value': 'test'}
                ]
            },
            {
                'MetricName': 'ProcessingTime',
                'Value': 120.5,
                'Unit': 'Seconds',
                'Dimensions': [
                    {'Name': 'Pipeline', 'Value': 'etl'},
                    {'Name': 'Environment', 'Value': 'test'}
                ]
            },
            {
                'MetricName': 'RecordCount',
                'Value': 1000,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'Dataset', 'Value': 'contracts'},
                    {'Name': 'Environment', 'Value': 'test'}
                ]
            }
        ]
        
        response = self.cloudwatch_client.put_metric_data(
            Namespace='DataQuality/Enterprise',
            MetricData=metrics
        )
        
        # Verify metrics were published
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    def test_cloudwatch_alarm_creation(self):
        """Test CloudWatch alarm creation"""
        # Create alarm for data quality score
        alarm_name = 'DataQualityScoreAlarm'
        
        self.cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription='Alarm when data quality score drops below 0.8',
            MetricName='DataQualityScore',
            Namespace='DataQuality/Enterprise',
            Statistic='Average',
            Period=300,
            EvaluationPeriods=2,
            Threshold=0.8,
            ComparisonOperator='LessThanThreshold',
            Dimensions=[
                {'Name': 'Dataset', 'Value': 'contracts'},
                {'Name': 'Environment', 'Value': 'test'}
            ]
        )
        
        # Verify alarm was created
        response = self.cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])
        assert len(response['MetricAlarms']) == 1
        assert response['MetricAlarms'][0]['AlarmName'] == alarm_name


class TestAWSCompleteIntegration:
    """Complete AWS integration tests"""
    
    @mock_aws
    @mock_aws
    @mock_aws
    @mock_aws
    @mock_aws
    def setup_method(self):
        """Setup all AWS mocks"""
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.sqs_client = boto3.client('sqs', region_name='us-east-1')
        self.sns_client = boto3.client('sns', region_name='us-east-1')
        self.cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
        
        # Setup resources
        self.bucket_name = 'test-integration-bucket'
        self.queue_name = 'test-integration-queue'
        self.topic_name = 'test-integration-topic'
        
        self.s3_client.create_bucket(Bucket=self.bucket_name)
        
        queue_response = self.sqs_client.create_queue(QueueName=self.queue_name)
        self.queue_url = queue_response['QueueUrl']
        
        topic_response = self.sns_client.create_topic(Name=self.topic_name)
        self.topic_arn = topic_response['TopicArn']
    
    def test_complete_aws_data_quality_workflow(self):
        """Test complete AWS data quality workflow"""
        # Step 1: Upload data to S3
        test_data = pd.DataFrame({
            'contract_id': ['C001', 'C002', 'C003'],
            'client_name': ['Client A', 'Client B', 'Client C'],
            'contract_value': [100000, 250000, 75000],
            'status': ['Active', 'Active', 'Pending']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_data.to_csv(tmp_file.name, index=False)
            self.s3_client.upload_file(tmp_file.name, self.bucket_name, 'raw-data/contracts.csv')
            os.unlink(tmp_file.name)
        
        # Step 2: Send processing message to SQS
        processing_message = {
            'bucket': self.bucket_name,
            'key': 'raw-data/contracts.csv',
            'operation': 'quality_assessment'
        }
        
        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(processing_message)
        )
        
        # Step 3: Process message (simulate Lambda function)
        response = self.sqs_client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1
        )
        
        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = json.loads(message['Body'])
            
            # Simulate data quality assessment
            quality_assessment = DataQualityAssessment()
            quality_report = quality_assessment.assess_quality(test_data)
            
            # Step 4: Publish results to SNS
            result_message = {
                'quality_score': quality_report['overall_score'],
                'record_count': len(test_data),
                'timestamp': '2024-01-01T12:00:00Z'
            }
            
            self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(result_message),
                Subject='Data Quality Assessment Complete'
            )
            
            # Step 5: Publish metrics to CloudWatch
            self.cloudwatch_client.put_metric_data(
                Namespace='DataQuality/Enterprise',
                MetricData=[
                    {
                        'MetricName': 'QualityScore',
                        'Value': quality_report['overall_score'],
                        'Unit': 'Percent',
                        'Dimensions': [
                            {'Name': 'Dataset', 'Value': 'contracts'},
                            {'Name': 'Environment', 'Value': 'test'}
                        ]
                    }
                ]
            )
            
            # Delete processed message
            self.sqs_client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
        
        # Verify workflow completion
        # Check S3 file exists
        s3_response = self.s3_client.head_object(Bucket=self.bucket_name, Key='raw-data/contracts.csv')
        assert s3_response['ContentLength'] > 0
        
        # Check queue is empty
        queue_response = self.sqs_client.receive_message(QueueUrl=self.queue_url)
        assert 'Messages' not in queue_response or len(queue_response['Messages']) == 0
