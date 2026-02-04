# Deployment Guide - AWS Serverless Pipeline

## Prerequisites Checklist

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI installed and configured
- [ ] Python 3.8+ installed
- [ ] Git installed

## Step-by-Step Deployment

### 1. Configure AWS CLI

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Output format (json)

### 2. Set Project Variables

```bash
# Set these variables for your project
export INPUT_BUCKET="your-project-input-bucket-$(date +%s)"
export OUTPUT_BUCKET="your-project-output-bucket-$(date +%s)"
export LAMBDA_ROLE_NAME="ServerlessPipelineLambdaRole"
export LAMBDA_FUNCTION_NAME="DataProcessingFunction"
export DYNAMODB_TABLE="ProcessingMetadata"
export AWS_REGION="us-east-1"
```

### 3. Create S3 Buckets

```bash
# Create input bucket
aws s3 mb s3://$INPUT_BUCKET --region $AWS_REGION

# Create output bucket
aws s3 mb s3://$OUTPUT_BUCKET --region $AWS_REGION

# Verify buckets created
aws s3 ls
```

### 4. Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name $DYNAMODB_TABLE \
    --attribute-definitions AttributeName=FileId,AttributeType=S \
    --key-schema AttributeName=FileId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $AWS_REGION

# Wait for table to be active
aws dynamodb wait table-exists --table-name $DYNAMODB_TABLE
```

### 5. Create IAM Role for Lambda

```bash
# Create trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
    --role-name $LAMBDA_ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create and attach custom policy
cat > lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::$INPUT_BUCKET/*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::$OUTPUT_BUCKET/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:$AWS_REGION:*:table/$DYNAMODB_TABLE"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name $LAMBDA_ROLE_NAME \
    --policy-name ServerlessPipelinePolicy \
    --policy-document file://lambda-policy.json

# Get role ARN (save this)
export LAMBDA_ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query 'Role.Arn' --output text)
echo "Lambda Role ARN: $LAMBDA_ROLE_ARN"

# Wait for role to propagate
sleep 10
```

### 6. Package Lambda Function

```bash
cd lambda

# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package
zip -r ../function.zip .

cd ..
```

### 7. Create Lambda Function

```bash
aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --runtime python3.9 \
    --role $LAMBDA_ROLE_ARN \
    --handler process_data.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 300 \
    --memory-size 512 \
    --environment Variables="{OUTPUT_BUCKET=$OUTPUT_BUCKET,DYNAMODB_TABLE=$DYNAMODB_TABLE}" \
    --region $AWS_REGION
```

### 8. Configure S3 Trigger

```bash
# Add permission for S3 to invoke Lambda
aws lambda add-permission \
    --function-name $LAMBDA_FUNCTION_NAME \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::$INPUT_BUCKET

# Create notification configuration
cat > s3-notification.json << EOF
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --query 'Configuration.FunctionArn' --output text)",
      "Events": ["s3:ObjectCreated:*"]
    }
  ]
}
EOF

# Apply notification configuration
aws s3api put-bucket-notification-configuration \
    --bucket $INPUT_BUCKET \
    --notification-configuration file://s3-notification.json
```

### 9. Test the Pipeline

```bash
# Create a test file
echo "Hello, this is a test file!" > test.txt

# Upload to input bucket
aws s3 cp test.txt s3://$INPUT_BUCKET/

# Wait a few seconds
sleep 5

# Check output bucket
aws s3 ls s3://$OUTPUT_BUCKET/processed/

# Check DynamoDB
aws dynamodb scan --table-name $DYNAMODB_TABLE

# View Lambda logs
aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow
```

## Updating Lambda Function

```bash
# Make changes to your code
cd lambda

# Recreate deployment package
zip -r ../function.zip .

cd ..

# Update function
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://function.zip
```

## Cleanup Resources

```bash
# Delete Lambda function
aws lambda delete-function --function-name $LAMBDA_FUNCTION_NAME

# Delete S3 buckets (first empty them)
aws s3 rm s3://$INPUT_BUCKET --recursive
aws s3 rb s3://$INPUT_BUCKET

aws s3 rm s3://$OUTPUT_BUCKET --recursive
aws s3 rb s3://$OUTPUT_BUCKET

# Delete DynamoDB table
aws dynamodb delete-table --table-name $DYNAMODB_TABLE

# Delete IAM role
aws iam delete-role-policy --role-name $LAMBDA_ROLE_NAME --policy-name ServerlessPipelinePolicy
aws iam detach-role-policy --role-name $LAMBDA_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name $LAMBDA_ROLE_NAME
```

## Troubleshooting

### Lambda function not triggering
- Check S3 bucket notification configuration
- Verify Lambda has permission to be invoked by S3
- Check CloudWatch logs for errors

### Permission errors
- Ensure IAM role has correct policies
- Wait a few minutes for IAM changes to propagate

### Files not appearing in output bucket
- Check Lambda execution logs in CloudWatch
- Verify OUTPUT_BUCKET environment variable is set correctly

## Monitoring

```bash
# View CloudWatch logs
aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow

# Get Lambda metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=$LAMBDA_FUNCTION_NAME \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum
```

## Next Steps

1. Customize the data processing logic in `process_data.py`
2. Add input validation
3. Implement error notifications (SNS)
4. Add data transformation based on file type
5. Set up CloudWatch alarms
6. Create CI/CD pipeline for automated deployments
