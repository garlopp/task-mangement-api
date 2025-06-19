import smtplib
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM

def send_task_share_email(recipient_email: str, task_title: str, share_link: str):
    """
    Sends an email with the task share link.
    This is a basic implementation. For production, consider using a more robust library
    and handling exceptions, templates, etc.
    """
    subject = f"Task Shared With You: {task_title}"
    body = f"""
    <p>Hello,</p>
    <p>A task titled "<strong>{task_title}</strong>" has been shared with you.</p>
    <p>You can view the task details by clicking the link below:</p>
    <p><a href="{share_link}">{share_link}</a></p>
    <p>This link will expire, so please view it at your convenience.</p>
    <p>Best regards,</p>
    <p>Task Management App</p>
    """
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Use TLS encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, recipient_email, msg.as_string())
        print(f"Share email sent to {recipient_email} for task: {task_title}")
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        # In a real app, you'd want more sophisticated error handling/logging