import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "nishantdesale1402@gmail.com"
EMAIL_PASS = "qcrm tyia pisy xhcl"


def send_html_email(to_email, patient_name, severity , file_path):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        msg["Subject"] = f"Patient {patient_name} - Severity Notification"

        # Load HTML Template & Replace Variables
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; text-align: center;">
                <h2 style="color: #333;">Patient: <span style="color: #4CAF50;">{patient_name}</span></h2>
                <p style="font-size: 16px; color: #555;">Severity Level: <strong>{severity}</strong></p>
                <p style="font-size: 16px; color: #555;">Attachement: <strong> Here is the report attached to the email</strong></p>

                {"<a href='https://your-app.com/notify' style='display: inline-block; background: #4CAF50; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;'>Notify Doctor</a>" if severity == 'moderate' else "<p style='color: #777;'>Notification is only sent for moderate severity.</p>"}

                <p style="margin-top: 20px; font-size: 12px; color: #777;">© 2024 Healthcare System</p>
            </div>
        </body>
        </html>
        """
        
        
        with open(file_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())  # Read file content
                encoders.encode_base64(part)  # Encode to base64
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                msg.attach(part)
                msg.attach(MIMEText(html_content, "html"))

        # Send Email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

