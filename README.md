# AWS Serverless Data Pipeline

## 📋 Project Overview

A serverless data processing pipeline built on AWS that automatically processes uploaded files using AWS Lambda, S3, and other AWS services. This project demonstrates a complete serverless architecture for data ingestion, processing, and storage.

## 🏗️ Architecture

```
S3 (Input Bucket) → Lambda Function → Processing → S3 (Output Bucket) → DynamoDB (Metadata)
```

## ✨ Features

- **Automatic Trigger**: Files uploaded to S3 automatically trigger the processing pipeline
- **Serverless Processing**: Uses AWS Lambda for compute with no server management
- **Scalable**: Automatically scales based on demand
- **Cost-Effective**: Pay only for what you use
- **Metadata Storage**: Stores processing metadata in DynamoDB
- **Error Handling**: Comprehensive error handling and logging with CloudWatch

## 🛠️ Technologies Used

- **AWS Lambda**: Serverless compute for processing
- **Amazon S3**: Object storage for input and output files
- **Amazon DynamoDB**: NoSQL database for metadata
- **AWS IAM**: Identity and access management
- **CloudWatch**: Logging and monitoring
- **Python 3.x**: Lambda function runtime

## 📁 Project Structure

```
aws-serverless-pipeline/
├── lambda/
│   ├── process_data.py          # Main Lambda function
│   └── requirements.txt          # Python dependencies
├── infrastructure/
│   └── iam_policy.json          # IAM policy template
├── tests/
│   └── test_lambda.py           # Unit tests
├── .gitignore
├── README.md
└── deployment_guide.md
```

## 🚀 Setup Instructions

### Prerequisites

- AWS Account
- AWS CLI configured with your credentials
- Python 3.8 or higher
- Basic knowledge of AWS services

### Step 1: Create S3 Buckets

```bash
# Create input bucket
aws s3 mb s3://your-input-bucket-name

# Create output bucket
aws s3 mb s3://your-output-bucket-name
```

### Step 2: Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name ProcessingMetadata \
    --attribute-definitions AttributeName=FileId,AttributeType=S \
    --key-schema AttributeName=FileId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### Step 3: Create IAM Role for Lambda

1. Go to IAM Console
2. Create a new role with Lambda as trusted entity
3. Attach the following policies:
   - AWSLambdaBasicExecutionRole
   - AmazonS3ReadOnlyAccess
   - AmazonS3FullAccess (for output bucket)
   - AmazonDynamoDBFullAccess

### Step 4: Deploy Lambda Function

1. Install dependencies:
```bash
cd lambda
pip install -r requirements.txt -t .
```

2. Create deployment package:
```bash
zip -r function.zip .
```

3. Create Lambda function:
```bash
aws lambda create-function \
    --function-name DataProcessingFunction \
    --runtime python3.9 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
    --handler process_data.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 300 \
    --memory-size 512
```

### Step 5: Configure S3 Trigger

```bash
aws s3api put-bucket-notification-configuration \
    --bucket your-input-bucket-name \
    --notification-configuration file://s3-notification.json
```

## 📝 Usage

1. Upload a file to the input S3 bucket:
```bash
aws s3 cp your-file.csv s3://your-input-bucket-name/
```

2. The Lambda function automatically processes the file

3. Check the output bucket for processed results:
```bash
aws s3 ls s3://your-output-bucket-name/
```

4. View metadata in DynamoDB:
```bash
aws dynamodb scan --table-name ProcessingMetadata
```

## 🔧 Configuration

Update the environment variables in the Lambda function:

- `OUTPUT_BUCKET`: Name of your output S3 bucket
- `DYNAMODB_TABLE`: Name of your DynamoDB table

## 📊 Monitoring

- View logs in CloudWatch Logs under `/aws/lambda/DataProcessingFunction`
- Monitor metrics in CloudWatch dashboard
- Set up CloudWatch alarms for errors

## 🧪 Testing

Run unit tests:
```bash
cd tests
python -m pytest test_lambda.py
```

## 💰 Cost Estimation

- **Lambda**: ~$0.20 per million requests
- **S3**: ~$0.023 per GB/month
- **DynamoDB**: Free tier covers 25 GB storage
- **CloudWatch**: Minimal costs for logging

## 🔐 Security Best Practices

- Use least privilege IAM policies
- Enable S3 bucket encryption
- Enable CloudWatch logging
- Use VPC for sensitive workloads
- Implement input validation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

  Dhanya Lokesh
- AWS Certified
- BCA Graduate

## 📧 Contact

- Email: ldhanya011@gmail.com
- LinkedIn: https://www.linkedin.com/in/dhanya-l-0aa510354
- GitHub: [@DhanyaLokeah-dev](https://github.com/DhanyaLokesh-dev)

---

⭐ If you found this project helpful, please give it a star!
