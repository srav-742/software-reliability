#!/usr/bin/env python3
"""
Software Reliability Platform - CI/CD CLI Client

Usage:
    python reliability_cli.py --api-url http://localhost:8000 --api-key sra_xyz123 --project-name "MyService"
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
import urllib.parse
import zipfile

# Force UTF-8 stdout encoding on Windows console if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Directories/files to exclude from zip archive
DEFAULT_EXCLUDES = {
    ".git", ".github", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".idea", ".vscode", "dist", "build", "coverage", ".env"
}


def safe_print(text: str):
    """Safely print text handling Windows charmap codec limitations."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback without emojis for standard cp1252 consoles
        clean_text = (
            text.replace("🛡️", "[SRA]")
            .replace("📦", "[ZIP]")
            .replace("🚀", "[RUN]")
            .replace("🟢", "[PASS]")
            .replace("🟡", "[WARN]")
            .replace("🔴", "[FAIL]")
            .replace("🚨", "[ALERT]")
            .replace("✅", "[OK]")
            .replace("❌", "[FAIL]")
        )
        print(clean_text)


def create_zip_archive(source_dir: str) -> str:
    """Zip source code directory into a temporary zip file, ignoring standard ignored folders."""
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_zip_path = temp_zip.name
    temp_zip.close()

    source_dir = os.path.abspath(source_dir)

    with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]

            for file in files:
                if file.endswith((".pyc", ".pyo", ".pyd", ".env", ".zip", ".tar.gz")):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    return temp_zip_path


def send_multipart_request(url: str, headers: dict, fields: dict, file_field: str, file_path: str) -> dict:
    """Send multipart/form-data HTTP POST request using standard library urllib."""
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()
    body = bytearray()

    # Append normal text form fields
    for key, value in fields.items():
        if value is None:
            continue
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{value}\r\n".encode("utf-8"))

    # Append file payload
    filename = os.path.basename(file_path)
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8")
    )
    body.extend(b"Content-Type: application/zip\r\n\r\n")

    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(url, data=bytes(body), method="POST")

    for k, v in headers.items():
        req.add_header(k, v)

    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
            detail = err_json.get("detail", str(e))
        except Exception:
            detail = err_body or str(e)
        safe_print(f"\033[91mAPI Error ({e.code}): {detail}\033[0m")
        sys.exit(1)
    except urllib.error.URLError as e:
        safe_print(f"\033[91mConnection Failed: {e.reason}\033[0m")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Software Reliability CI/CD Scan Client")
    parser.add_argument("--api-url", default=os.getenv("RELIABILITY_API_URL", "http://localhost:8000"), help="API base URL")
    parser.add_argument("--api-key", default=os.getenv("RELIABILITY_API_KEY"), help="Software Reliability API Key")
    parser.add_argument("--project-id", type=int, default=os.getenv("RELIABILITY_PROJECT_ID"), help="Existing Project ID")
    parser.add_argument("--project-name", default=os.getenv("RELIABILITY_PROJECT_NAME"), help="Project Name")
    parser.add_argument("--fail-threshold", type=float, default=float(os.getenv("RELIABILITY_FAIL_THRESHOLD", "80.0")), help="Risk score threshold to FAIL build")
    parser.add_argument("--warn-threshold", type=float, default=float(os.getenv("RELIABILITY_WARN_THRESHOLD", "50.0")), help="Risk score threshold for WARN status")
    parser.add_argument("--path", default=".", help="Source code root directory to analyze")
    parser.add_argument("--commit-sha", default=os.getenv("GITHUB_SHA", "local-dev"), help="Git Commit SHA")
    parser.add_argument("--branch", default=os.getenv("GITHUB_REF_NAME", "main"), help="Git Branch")
    parser.add_argument("--author", default=os.getenv("GITHUB_ACTOR", "Local Developer"), help="Commit Author")

    args = parser.parse_args()

    if not args.api_key:
        safe_print("\033[91mError: API Key is required. Set --api-key or RELIABILITY_API_KEY environment variable.\033[0m")
        sys.exit(1)

    safe_print("\033[94m=====================================================\033[0m")
    safe_print("\033[94m 🛡️ Software Reliability CI/CD Automated Analyzer   \033[0m")
    safe_print("\033[94m=====================================================\033[0m")
    safe_print(f" Target Path       : {os.path.abspath(args.path)}")
    safe_print(f" Target API        : {args.api_url}")
    safe_print(f" Commit / Branch   : {args.commit_sha[:7]} ({args.branch})")
    safe_print(f" Policy Thresholds : Pass < {args.warn_threshold}% | Fail > {args.fail_threshold}%")
    safe_print("-----------------------------------------------------")
    safe_print(" 📦 Bundling source code into archive...")

    zip_path = create_zip_archive(args.path)

    try:
        safe_print(" 🚀 Uploading and executing ML Reliability Analysis...")
        scan_url = f"{args.api_url.rstrip('/')}/api/v1/cicd/scan"
        headers = {"X-API-Key": args.api_key}
        fields = {
            "project_id": str(args.project_id) if args.project_id else None,
            "project_name": args.project_name or os.path.basename(os.path.abspath(args.path)),
            "commit_sha": args.commit_sha,
            "branch": args.branch,
            "author": args.author,
            "pass_threshold": str(args.warn_threshold),
            "warn_threshold": str(args.fail_threshold),
        }

        result = send_multipart_request(scan_url, headers, fields, "source_code_file", zip_path)

        status = result.get("status", "UNKNOWN")
        risk_score = result.get("risk_score", 0.0)
        failure_prob = result.get("failure_probability", 0.0)
        report_md = result.get("report_markdown", "")
        exit_code = result.get("exit_code", 0)

        # Terminal Formatting
        if status == "PASS":
            color = "\033[92m"  # Green
            badge = "🟢 PASS"
        elif status == "WARN":
            color = "\033[93m"  # Yellow
            badge = "🟡 WARN"
        else:
            color = "\033[91m"  # Red
            badge = "🔴 FAIL"

        safe_print("\n\033[94m=====================================================\033[0m")
        safe_print(f" {color}BUILD STATUS: {badge}\033[0m")
        safe_print(f" Risk Score          : {color}{risk_score}%\033[0m")
        safe_print(f" Failure Probability : {failure_prob:.4f}")
        safe_print("\033[94m=====================================================\033[0m")

        recs = result.get("recommendations", [])
        if recs:
            safe_print("\n🚨 Actionable Recommendations:")
            for r in recs[:3]:
                if isinstance(r, dict):
                    safe_print(f"  • [{r.get('severity', 'HIGH')}] {r.get('issue')} -> {r.get('action')}")
                else:
                    safe_print(f"  • {r}")

        # Write to GitHub Step Summary if running in GitHub Actions
        github_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
        if github_summary_path and report_md:
            with open(github_summary_path, "a", encoding="utf-8") as f:
                f.write(report_md + "\n")
            safe_print("\n ✅ GitHub Step Summary written successfully.")

        if exit_code != 0:
            safe_print(f"\n\033[91m ❌ Build FAILED: Risk score ({risk_score}%) breached policy maximum threshold ({args.fail_threshold}%).\033[0m")
            sys.exit(1)
        else:
            safe_print(f"\n\033[92m ✅ Build PASSED policy evaluation.\033[0m")
            sys.exit(0)

    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)


if __name__ == "__main__":
    main()
