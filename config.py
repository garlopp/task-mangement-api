SECRET_KEY = "blueface2580"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Base URL for the application (e.g., for generating share links)
APP_BASE_URL = "http://localhost:8000"  # Change this to your actual domain in production

# Email sending configuration (replace with your actual SMTP server details)
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@example.com"
SMTP_PASSWORD = "your-email-password"
EMAIL_FROM = "noreply@example.com"