import json
import os
import smtplib
from email.message import EmailMessage

with open("test-report.json", encoding="utf-8") as f:
    r = json.load(f)

s = r["summary"]
lines = [
    f"Repository : {r['repository']}",
    f"Branch     : {r['branch']}",
    f"Commit     : {r['commit_sha']}",
    f"Run ID     : {r['pipeline_run_id']}",
    f"Executed   : {r['executed_at']}",
    f"Overall    : {r['status'].upper()}",
    f"Total/Passed/Failed: {s['total']}/{s['passed']}/{s['failed']}",
    "",
    "Individual results:",
]
for t in r["tests"]:
    line = f"  [{t['result'].upper()}] {t['name']}"
    if t["failure_message"]:
        line += f"\n      {t['failure_message']}"
    lines.append(line)

msg = EmailMessage()
msg["Subject"] = f"[{r['status'].upper()}] {r['repository']} @ {r['commit_sha'][:7]}"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["REPORT_TO"]
msg.set_content("\n".join(lines))
msg.add_attachment(
    json.dumps(r, indent=2).encode(),
    maintype="application",
    subtype="json",
    filename="test-report.json",
)

with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], 465) as server:
    server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
    server.send_message(msg)

print("Email sent")