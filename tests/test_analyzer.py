import sys
import os
import pytest

# --- Fix imports so pytest finds analyzer.py ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from analyzer import compare_resources, analyze_resources


def test_match_resources():
    cloud = {
        "type": "aws_instance",
        "id": "i-123",
        "tags": {"Name": "web", "Env": "prod"},
        "instance_type": "t3.micro",
    }
    iac = {
        "type": "aws_instance",
        "id": "i-123",
        "tags": {"Env": "prod", "Name": "web"},  # order shouldn’t matter
        "instance_type": "t3.micro",
    }

    result = compare_resources(cloud, iac)

    assert result["State"] == "Match"
    assert result["ChangeLog"] == []


def test_modified_resources():
    cloud = {
        "type": "aws_instance",
        "id": "i-123",
        "instance_type": "t3.small",
        "ami": "ami-abc",
    }
    iac = {
        "type": "aws_instance",
        "id": "i-123",
        "instance_type": "t3.micro",  # different
        "ami": "ami-abc",
    }

    result = compare_resources(cloud, iac)

    assert result["State"] == "Modified"
    assert any(change["KeyName"] == "instance_type" for change in result["ChangeLog"])


def test_missing_iac_resource():
    cloud = {
        "type": "aws_s3_bucket",
        "id": "my-logs",
        "public": True,
    }
    iac = None  # not found in IaC

    result = compare_resources(cloud, iac)

    assert result["State"] == "Missing"
    assert result["ChangeLog"] == []


def test_analyze_resources_full_flow():
    cloud_resources = {
        "resources": [
            {"type": "aws_instance", "id": "i-123", "instance_type": "t3.micro"},
            {"type": "aws_db_instance", "id": "prod-db-1", "engine": "postgres", "publicly_accessible": True},
            {"type": "aws_s3_bucket", "id": "my-logs", "public": True},
        ]
    }

    iac_resources = {
        "resources": [
            {"type": "aws_instance", "id": "i-123", "instance_type": "t3.micro"},
            {"type": "aws_db_instance", "id": "prod-db-1", "engine": "postgres", "publicly_accessible": False},
            # no S3 bucket here -> should be Missing
        ]
    }

    results = analyze_resources(cloud_resources, iac_resources)

    states = [r["State"] for r in results]
    assert "Match" in states
    assert "Modified" in states
    assert "Missing" in states
    assert len(results) == 3
