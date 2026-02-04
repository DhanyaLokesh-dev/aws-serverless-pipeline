import json
import boto3
import os
from datetime import datetime
import logging

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'your-output-bucket-name')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ProcessingMetadata')

def lambda_handler(event, context):
    """
    Main Lambda handler function triggered by S3 upload
    
    Args:
        event: S3 event data
        context: Lambda context
    
    Returns:
        dict: Response with status code and message
    """
    try:
        # Extract bucket and file information from event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        file_size = event['Records'][0]['s3']['object']['size']
        
        logger.info(f"Processing file: {file_key} from bucket: {bucket_name}")
        
        # Download file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read()
        
        # Process the data
        processed_data = process_data(file_content)
        
        # Upload processed data to output bucket
        output_key = f"processed/{file_key}"
        upload_to_s3(processed_data, output_key)
        
        # Store metadata in DynamoDB
        store_metadata(file_key, file_size, output_key)
        
        logger.info(f"Successfully processed file: {file_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File processed successfully',
                'input_file': file_key,
                'output_file': output_key
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing file',
                'error': str(e)
            })
        }

def process_data(file_content):
    """
    Process the file content
    
    Args:
        file_content: Raw file content
    
    Returns:
        str: Processed data
    """
    try:
        # Decode content
        data = file_content.decode('utf-8')
        
        # Example processing: Convert to uppercase and add timestamp
        processed = data.upper()
        timestamp = datetime.now().isoformat()
        
        result = f"Processed at: {timestamp}\n\n{processed}"
        
        logger.info("Data processing completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in data processing: {str(e)}")
        raise

def upload_to_s3(data, file_key):
    """
    Upload processed data to S3 output bucket
    
    Args:
        data: Processed data to upload
        file_key: S3 key for the file
    """
    try:
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=file_key,
            Body=data.encode('utf-8'),
            ContentType='text/plain'
        )
        logger.info(f"Uploaded processed file to: {OUTPUT_BUCKET}/{file_key}")
        
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        raise

def store_metadata(input_file, file_size, output_file):
    """
    Store processing metadata in DynamoDB
    
    Args:
        input_file: Input file key
        file_size: Size of input file
        output_file: Output file key
    """
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        item = {
            'FileId': input_file,
            'InputFile': input_file,
            'OutputFile': output_file,
            'FileSize': file_size,
            'ProcessedAt': datetime.now().isoformat(),
            'Status': 'SUCCESS'
        }
        
        table.put_item(Item=item)
        logger.info(f"Metadata stored in DynamoDB for file: {input_file}")
        
    except Exception as e:
        logger.error(f"Error storing metadata: {str(e)}")
        # Don't raise - we don't want to fail the entire process if metadata storage fails
