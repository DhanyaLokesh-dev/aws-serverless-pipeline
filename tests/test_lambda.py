import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the lambda directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lambda'))

from process_data import lambda_handler, process_data, upload_to_s3, store_metadata


class TestLambdaFunction(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-input-bucket'},
                    'object': {
                        'key': 'test-file.txt',
                        'size': 1024
                    }
                }
            }]
        }
        
        self.sample_context = Mock()
    
    def test_process_data(self):
        """Test data processing function"""
        input_data = b"hello world"
        result = process_data(input_data)
        
        self.assertIn("HELLO WORLD", result)
        self.assertIn("Processed at:", result)
    
    @patch('process_data.s3_client')
    @patch('process_data.dynamodb')
    def test_lambda_handler_success(self, mock_dynamodb, mock_s3):
        """Test successful Lambda execution"""
        # Mock S3 get_object
        mock_s3.get_object.return_value = {
            'Body': Mock(read=Mock(return_value=b"test data"))
        }
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        # Execute Lambda
        response = lambda_handler(self.sample_event, self.sample_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'File processed successfully')
    
    @patch('process_data.s3_client')
    def test_lambda_handler_error(self, mock_s3):
        """Test Lambda error handling"""
        # Make S3 throw an error
        mock_s3.get_object.side_effect = Exception("S3 Error")
        
        # Execute Lambda
        response = lambda_handler(self.sample_event, self.sample_context)
        
        # Assertions
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'Error processing file')


if __name__ == '__main__':
    unittest.main()
