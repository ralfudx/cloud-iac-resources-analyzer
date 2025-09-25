# LocalStack image for cloud-iac-analyzer
FROM localstack/localstack:latest

# Copy init script into container (for bucket creation)
COPY init-s3.sh /etc/localstack/init/ready.d/init-s3.sh

# Ensure script is executable
RUN chmod +x /etc/localstack/init/ready.d/init-s3.sh
