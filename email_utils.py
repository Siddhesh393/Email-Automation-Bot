import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
password = os.getenv("EMAIL_PASSWORD")


def load_template(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def send_email(role, emails):
    try:
        template_map = {
            "ai/ml": "templates/ai_ml.txt",
            "data analyst": "templates/data_analyst.txt"
        }

        resume_map = {
            "ai/ml": "resumes/ai_ml.pdf",
            "data analyst": "resumes/data_analyst.pdf"
        }

        body = load_template(template_map[role])

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = sender_email
        msg["Subject"] = "Application for Opportunity"

        # 📩 Email body
        msg.attach(MIMEText(body, "plain"))

        # 📎 Attachment (Resume)
        resume_path = resume_map[role]

        with open(resume_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        filename = os.path.basename(resume_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )

        msg.attach(part)

        try:

            print("Connecting to SMTP...")

            server = smtplib.SMTP_SSL(
                "smtp.zoho.in",
                465,
                timeout=30
            )

            print("Logging in...")

            server.login(sender_email, password)

            print("SMTP Login Successful")

            print("Sending email...")

            emails = [email.strip() for email in emails if email.strip()]
            
            server.sendmail(
                sender_email,
                emails,
                msg.as_string()
            )

            print("Email Sent Successfully")

            server.quit()

        except Exception as e:
            print("SMTP ERROR:", e)
            return f"FAILED: {str(e)}"
        
        return "SUCCESS"

    except Exception as e:
        return f"FAILED: {str(e)}"