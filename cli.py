import argparse
import json
from analyzer import load_json, analyze_resources, summarize_analysis, upload_report_to_s3

def main():
    p = argparse.ArgumentParser(description="Cloud -> IaC resources analyzer")
    p.add_argument("--cloud", required=True, help="Path to cloud resources JSON")
    p.add_argument("--iac", required=True, help="Path to IaC resources JSON")
    p.add_argument("--out", default="analysis_output.json", help="Path to write analyzer output")
    p.add_argument("--s3-bucket", help="Upload report directly to this S3 bucket")
    p.add_argument("--s3-key", default="report.json", help="S3 key for the report")
    p.add_argument("--s3-endpoint", default="http://localhost:4566", help="S3 endpoint (LocalStack)")
    args = p.parse_args()

    cloud = load_json(args.cloud)
    iac = load_json(args.iac)

    analysis = analyze_resources(cloud, iac)
    summary = summarize_analysis(analysis)
    report = {
        "analysis": analysis,
        "summary": summary
    }

    print(json.dumps(report, indent=2))

    print("Done. Summary:", summary)
    print("Wrote:", args.out)

    if args.s3_bucket:
        upload_report_to_s3(report, args.s3_bucket, args.s3_key, args.s3_endpoint)

if __name__ == "__main__":
    main()
