# 🧩 Cloud → IaC Resources Analyzer

This project analyzes discrepancies between **actual cloud resources** and their corresponding **Infrastructure-as-Code (IaC)** definitions.  
It helps detect drift, inconsistencies, and missing resources. The analyzer can also upload reports into a **LocalStack-hosted S3 bucket** for further inspection.

---

## 📂 Project Structure
```bash
cloud-iac-analyzer/
├─ analyzer.py           # Core logic (comparison, normalization, S3 uploader)
├─ cli.py                # Command-line interface
├─ sample/
│  ├─ cloud_resources.json   # Example exported cloud resources
│  └─ iac_resources.json     # Example IaC resource definitions
├─ tests/
│  └─ test_analyzer.py       # Unit tests
├─ localstack/
│  ├─ Dockerfile             # Custom LocalStack image with S3 bucket setup
│  ├─ docker-compose.yml     # LocalStack service runner
│  └─ init-s3.sh             # Init script: creates S3 bucket `analyzer-reports`
├─ Makefile                  # Automation commands
└─ README.md                 # Project documentation
```

---

## ⚙️ Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ralfudx/cloud-iac-resources-analyzer.git
   cd cloud-iac-resources-analyzer
   ```

2. **Install dependencies**:
   
   Create a Python venv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## ▶️ Running the Analyzer

1. **Basic Run (Console Output Only)**
    ```bash
    python cli.py --cloud resources/cloud_resources.json --iac resources/iac_resources.json
    ```

2. **Upload Report Directly to LocalStack S3**
    ```bash
    python cli.py \
        --cloud sample/cloud_resources.json \
        --iac sample/iac_resources.json \
        --s3-bucket analyzer-reports \
        --s3-key report.json \
        --s3-endpoint http://localhost:4566
    ```

---

## 🛠️ Using the Makefile

Handy shortcuts are provided:

- Start LocalStack
    ```bash
    make up


- Stop LocalStack
    ```bash
    make down


- Generate Report & Upload to S3 (via boto3)
    ```bash
    make upload-direct


- List Files in Bucket
    ```bash
    make list


- Run Full Workflow (Start → Upload → List)
    ```bash
    make all


- Run Full Workflow & push report to s3 (Start → Upload-direct → List)
    ```bash
    make all-direct

---

## 🔎 Example Analysis Output
```bash
{
  "CloudResourceItem": {
    "type": "aws_instance",
    "name": "ec2_webserver",
    "volumes": [{"id": "vol-0a1b2c", "encrypted": false}]
  },
  "IacResourceItem": {
    "type": "aws_instance",
    "name": "ec2_webserver",
    "volumes": [{"id": "vol-0a1b2c", "encrypted": true}]
  },
  "State": "Modified",
  "ChangeLog": [
    {
      "KeyName": "volumes[0].encrypted",
      "CloudValue": false,
      "IacValue": true
    }
  ]
}
```

---


## 🧪 Running Tests

This project uses pytest for unit testing.

Run all tests:
```bash
pytest tests/
```


Example output:
```bash
===================== test session starts =====================
collected 3 items

tests/test_analyzer.py ...                               [100%]

====================== 3 passed in 0.42s ======================
```

---

## 🔨 Modifications Made

- Comparator Enhancements:

    - Canonicalize shapes (e.g., tag lists → dict).

    - Ignore provider-managed attributes (timestamps, ARNs, etc.).

    - Normalize data types for consistent comparison.

- LocalStack Integration:

    - Added Dockerfile to run LocalStack with a pre-created S3 bucket.

    - Analyzer reports can be uploaded directly to S3 via boto3 for persistence.

- Improved Readability:

    - Clear project structure.

    - Sample input JSON files provided.

    - Test suite included.

    - `Makefile` with common commands

---

## 💡 Recommendations & Enhancements

- Add web UI (Flask/FastAPI + JSON viewer) for interactive drift visualization.

- Extend analyzer to cover multi-cloud providers (AWS, Azure, GCP).

- Integrate with CI/CD pipelines to automatically detect and fail on drift.

- Provide exporters (HTML/Markdown reports) for easier sharing.

- Add Terraform state file support for more accurate comparisons.


---

## 📌 Other Information

- Python ≥ 3.9 recommended.

- LocalStack ≥ 3.x for AWS service emulation.

- Compatible with AWS CLI if configured against LocalStack (--endpoint-url http://localhost:4566).


---

## 📜 License

MIT License © 2025 — Use, modify, and share freely.

---
