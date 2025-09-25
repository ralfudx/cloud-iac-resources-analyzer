# Variables
DOCKER_COMPOSE = docker-compose -f localstack/docker-compose.yml
AWS = aws --endpoint-url=http://localhost:4566
REPORT_FILE = report.json
BUCKET = analyzer-reports

# Start LocalStack
up:
	$(DOCKER_COMPOSE) up -d
	@echo "✅ LocalStack started."

# Stop LocalStack
down:
	$(DOCKER_COMPOSE) down
	@echo "🛑 LocalStack stopped."

# Build LocalStack image
build:
	cd localstack && docker build -t localstack-iac .
	@echo "🔨 LocalStack image built."

# Generate analyzer report
report:
	python cli.py --cloud resources/cloud_resources.json --iac resources/iac_resources.json > $(REPORT_FILE)
	@echo "📄 Analyzer report generated: $(REPORT_FILE)"

# Upload report to S3
upload: report
	$(AWS) s3 cp $(REPORT_FILE) s3://$(BUCKET)/$(REPORT_FILE)
	@echo "☁️ Report uploaded to S3 bucket: $(BUCKET)/$(REPORT_FILE)"

# List files in the bucket
list:
	$(AWS) s3 ls s3://$(BUCKET)/

# Full workflow: start -> build report -> upload
all: up upload list

# Upload using analyzer (boto3, no aws cli needed)
upload-direct:
	python cli.py --cloud resources/cloud_resources.json --iac resources/iac_resources.json \
		--s3-bucket analyzer-reports --s3-key report.json --s3-endpoint http://localhost:4566

# Full workflow with boto3: start -> build report -> upload using analyzer
all-direct: up upload-direct
