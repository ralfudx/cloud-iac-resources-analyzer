#!/bin/bash
set -e

# Create S3 bucket at container startup
awslocal s3 mb s3://analyzer-reports

echo "✅ S3 bucket 'analyzer-reports' created."
