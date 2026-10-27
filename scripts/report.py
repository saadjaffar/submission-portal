import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def parse_junit(path="junit.xml"):
    if not os.path.exists(path):
        return []
    tests = []
    for case in ET.parse(path).getroot().iter("testcase"):
        result, message = "passed", None
        for tag in ("failure", "error"):
            node = case.find(tag)
            if node is not None:
                result = "failed"
                message = node.get("message") or (node.text or "").strip()
                break
        if case.find("skipped") is not None:
            result = "skipped"
        tests.append({"name": case.get("name"), "result": result,
                      "failure_message": message})
    return tests


def main():
    tests = parse_junit()
    passed = sum(t["result"] == "passed" for t in tests)
    failed = sum(t["result"] == "failed" for t in tests)
    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "summary": {"total": len(tests), "passed": passed, "failed": failed},
        "status": "passed" if tests and failed == 0 else "failed",
    }
    with open("test-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

    url = os.environ.get("RECEIVER_URL")
    if not url:
        print("RECEIVER_URL not set, skipping delivery.")
        return
    req = urllib.request.Request(
        url,
        data=json.dumps(report).encode(),
        headers={
            "Content-Type": "application/json",
            "X-Token": os.environ.get("RECEIVER_TOKEN", ""),
            "ngrok-skip-browser-warning": "true",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print("Receiver responded:", resp.status)
    except Exception as exc:
        print("WARNING: could not deliver report:", exc)


if __name__ == "__main__":
    main()