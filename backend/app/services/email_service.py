import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM or settings.SMTP_USER
        self.email_from_name = settings.EMAIL_FROM_NAME
        self.frontend_url = settings.FRONTEND_URL
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        """Send an email using SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("Email service not configured. Email would be sent to: %s", to_email)
            logger.warning("Subject: %s", subject)
            logger.warning("Content: %s", text_content or html_content)
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.email_from_name} <{self.email_from}>"
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, username: str, verification_token: str):
        """Send email verification link"""
        verification_url = f"{self.frontend_url}/verify-email?token={verification_token}"
        
        subject = "Verify Your SuryaDrishti Account"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to SuryaDrishti!</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Thank you for signing up for SuryaDrishti! Please verify your email address to activate your account.</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't create an account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 SuryaDrishti. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to SuryaDrishti!
        
        Hi {username},
        
        Thank you for signing up! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        © 2025 SuryaDrishti
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str):
        """Send password reset link"""
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        
        subject = "Reset Your SuryaDrishti Password"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #f59e0b 0%, #ef4444 50%, #ec4899 100%); color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_url}</p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 SuryaDrishti. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hi {username},
        
        We received a request to reset your password. Click the link below:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        © 2025 SuryaDrishti
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

email_service = EmailService()



