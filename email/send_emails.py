import smtplib
import csv
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# ==== CONFIGURATION ====
SMTP_SERVER = "smtp.gmail.com"       # Gmail SMTP server
SMTP_PORT = 587                      # TLS port
EMAIL_ADDRESS = "csmyatnoe98@gmail.com"
EMAIL_PASSWORD = "rbxc clhe zhcl rwsf" # Use an App Password for Gmail
RESUME_FILE = "Resume - Ms. Chit Su Myat Noe.pdf"
COVER_LETTER_FILE = "Cover Letter - Ms. Chit Su Myat Noe.pdf"
CSV_FILE = "recipients.csv"
EMAIL_TEMPLATE = "email_body.txt"
SUBJECT_TEMPLATE = "Application for {Position}"
DELAY_SECONDS = 120  # 2 minutes between emails
# ========================

def send_email(to_email, position):
    # Read email body and replace placeholders
    with open(EMAIL_TEMPLATE, "r", encoding="utf-8") as f:
        body = f.read().format(Position=position)

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = SUBJECT_TEMPLATE.format(Position=position)

    msg.attach(MIMEText(body, 'plain'))

    # Attach resume and cover letter
    for file_path in [RESUME_FILE, COVER_LETTER_FILE]:
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                msg.attach(part)

    # Send via SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"[✓] Email sent to {to_email}")

def main():
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            send_email(row['Email'], row['Position'])
            print(f"Waiting {DELAY_SECONDS} seconds before next email...")
            time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    main()
