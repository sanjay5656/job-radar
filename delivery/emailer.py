import os
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

    rows = ""
    for job_id, title, company, location, url, score, reason in jobs:
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee;">
                <b>{title}</b><br>{company} — {location}<br>
                <a href="{url}">View posting</a><br>
                <span style="color:#555;font-size:13px;">{reason}</span>
            </td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">
                <b>{score}%</b>
            </td>
        </tr>
        """

    html = f"""
    <html><body>
    <h2>Your Job Radar Digest</h2>
    <table style="width:100%;border-collapse:collapse;">
        <tr><th>Job</th><th>Match</th></tr>
        {rows}
    </table>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Job Radar: {len(jobs)} new matches"
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_email, msg.as_string())

    print(f"Sent digest with {len(jobs)} jobs.")