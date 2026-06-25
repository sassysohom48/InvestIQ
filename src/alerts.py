import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_alert_email(to_email: str, subject: str, body_html: str) -> tuple[bool, str]:
    if not to_email or to_email.endswith(".local"):
        return False, "Invalid email address"
        
    try:
        sender_email = st.secrets["email"]["sender_email"]
        app_password = st.secrets["email"]["app_password"].replace(" ", "")
    except Exception as e:
        # Secrets not configured
        return False, f"Secrets error: {e}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body_html, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True, ""
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, str(e)
