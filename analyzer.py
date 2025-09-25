import boto3
import json
import os
from typing import Any, Dict, List


# Keys we want to ignore (provider-managed, not IaC-controlled)
IGNORED_KEYS = {"arn", "id", "owner_id", "creation_date", "last_modified", "etag"}


def should_compare(key: str) -> bool:
    return key not in IGNORED_KEYS


def normalize_tags(value: Any) -> Dict[str, str]:
    """Normalize tags into a dict format."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, list):
        normalized = {}
        for item in value:
            if isinstance(item, dict):
                k = item.get("Key") or item.get("key")
                v = item.get("Value") or item.get("value")
                if k is not None:
                    normalized[str(k)] = str(v)
        return normalized
    return {}


def normalize_value(val: Any) -> Any:
    """Normalize values for fair comparison."""
    if val is None:
        return None

    if isinstance(val, str):
        lower = val.lower()
        if lower == "true":
            return True
        if lower == "false":
            return False
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val.strip()

    if isinstance(val, list):
        return [normalize_value(v) for v in val]

    if isinstance(val, dict):
        if "Key" in val or "key" in val:
            return normalize_tags([val])
        return {k: normalize_value(v) for k, v in val.items() if should_compare(k)}

    return val


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dicts into dotted keys."""
    items = []
    for k, v in d.items():
        if not should_compare(k):
            continue
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, normalize_value(v)))
    return dict(items)


def compare_resources(cloud: Dict[str, Any], iac: Dict[str, Any]) -> Dict[str, Any]:
    """Compare one cloud resource with its matching IaC resource."""
    if iac is None:
        return {
            "CloudResourceItem": cloud,
            "IacResourceItem": {},
            "State": "Missing",
            "ChangeLog": []
        }

    cloud_flat = flatten_dict(cloud)
    iac_flat = flatten_dict(iac)

    if "tags" in cloud:
        cloud_flat["tags"] = normalize_tags(cloud.get("tags"))
    if "tags" in iac:
        iac_flat["tags"] = normalize_tags(iac.get("tags"))

    changes: List[Dict[str, Any]] = []
    all_keys = set(cloud_flat.keys()) | set(iac_flat.keys())

    for key in all_keys:
        cloud_val = cloud_flat.get(key)
        iac_val = iac_flat.get(key)
        if cloud_val != iac_val:
            changes.append({
                "KeyName": key,
                "CloudValue": cloud_val,
                "IacValue": iac_val
            })

    state = "Match" if not changes else "Modified"

    return {
        "CloudResourceItem": cloud,
        "IacResourceItem": iac,
        "State": state,
        "ChangeLog": changes
    }


# def analyze_resources(
#     cloud_resources: List[Dict[str, Any]],
#     iac_resources: List[Dict[str, Any]]
# ) -> List[Dict[str, Any]]:
#     """Compare all cloud resources against IaC resources."""
#     results = []
#     for cloud_res in cloud_resources:
#         match = next(
#             (
#                 iac for iac in iac_resources
#                 if iac.get("type") == cloud_res.get("type")
#                 and iac.get("name") == cloud_res.get("name")
#             ),
#             None
#         )
#         results.append(compare_resources(cloud_res, match))
#     return results

def analyze_resources(cloud_resources: dict, iac_resources: dict) -> list:
    results = []
    for cloud_res in cloud_resources.get("resources", []):
        match = next(
            (
                iac for iac in iac_resources.get("resources", [])
                if isinstance(iac, dict)
                and iac.get("type") == cloud_res.get("type")
                and iac.get("id") == cloud_res.get("id")
            ),
            None,
        )
        results.append(compare_resources(cloud_res, match))
    return results


def load_json(path: str) -> Dict[str, Any]:
    """Utility: load a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def summarize_analysis(results: List[Dict[str, Any]]) -> Dict[str, int]:
    """Summarize analyzer results by state."""
    summary = {"Match": 0, "Modified": 0, "Missing": 0}
    for res in results:
        summary[res["State"]] = summary.get(res["State"], 0) + 1
    return summary

def upload_report_to_s3(report: dict, bucket: str, key: str, endpoint_url: str = None):
    """
    Upload the analyzer report to an S3 bucket.

    :param report: The report object (dict)
    :param bucket: Target S3 bucket name
    :param key: S3 key (filename in bucket)
    :param endpoint_url: Optional S3 endpoint (useful for LocalStack)
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        endpoint_url=endpoint_url,
    )

    # Ensure the report is JSON-serialized
    body = json.dumps(report, indent=2)

    s3.put_object(Bucket=bucket, Key=key, Body=body.encode("utf-8"))

    print(f"✅ Report uploaded to s3://{bucket}/{key}")
