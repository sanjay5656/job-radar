import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_digest(jobs):
    if not jobs:
        print("No jobs to send.")
        return

    gmail_user = os.environ["GMAIL_ADDRESS"]
    gmail_pass = os.environ["GMAIL_APP_PASSWORD"]
    to_email = os.environ.get("EMAIL_TO", gmail_user)

    blocks = ""
    for job_id, title, company, location, url, score, summary, ats_json, missing_json in jobs:
        ats_keywords = json.loads(ats_json) if ats_json else []
        missing_keywords = json.loads(missing_json) if missing_json else []

        ats_html = "".join(f'<span style="background:#eef;padding:3px 8px;margin:2px;border-radius:4px;font-size:12px;display:inline-block;">{k}</span>' for k in ats_keywords)
        missing_html = "".join(f'<span style="background:#fee;padding:3px 8px;margin:2px;border-radius:4px;font-size:12px;display:inline-block;">{k}</span>' for k in missing_keywords)

        blocks += f"""
        <div style="border:1px solid #ddd;border-radius:8px;padding:14px;margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;">
                <b style="font-size:16px;">{title}</b>
                <b style="font-size:16px;color:#2a7;">{score}%</b>
            </div>
            <div style="color:#555;font-size:13px;margin-bottom:8px;">{company} — {location}</div>
            <div style="font-size:13px;margin-bottom:8px;">{summary}</div>
            <div style="margin-bottom:6px;"><b style="font-size:12px;">ATS keywords:</b><br>{ats_html}</div>
            {f'<div style="margin-bottom:6px;"><b style="font-size:12px;">Missing from resume:</b><br>{missing_html}</div>' if missing_keywords else ''}
            <a href="{url}" style="font-size:13px;">View posting →</a>
        </div>
        """

    html = f"<html><body><h2>Your Job Radar Digest</h2>{blocks}</body></html>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Radar: {len(jobs)} new matches"
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_email, msg.as_string())

    print(f"Sent digest with {len(jobs)} jobs.")