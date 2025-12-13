"""
Custom email backend for Resend API
Works on Render free tier (no SMTP ports needed)
"""
import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend using Resend HTTP API instead of SMTP
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set API key from settings
        resend.api_key = settings.RESEND_API_KEY
    
    def send_messages(self, email_messages):
        """
        Send emails using Resend HTTP API
        """
        if not email_messages:
            return 0
        
        num_sent = 0
        
        for message in email_messages:
            try:
                # Prepare email parameters
                params = {
                    "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                    "to": message.to,
                    "subject": message.subject,
                }
                
                # Add CC if present
                if message.cc:
                    params["cc"] = message.cc
                
                # Add BCC if present
                if message.bcc:
                    params["bcc"] = message.bcc
                
                # Add reply_to if present
                if message.reply_to:
                    params["reply_to"] = message.reply_to
                
                # Handle HTML vs plain text
                if message.content_subtype == 'html':
                    params["html"] = message.body
                else:
                    params["text"] = message.body
                
                # Send via Resend API
                response = resend.Emails.send(params)
                
                if not self.fail_silently and hasattr(response, 'get') and response.get('error'):
                    raise Exception(f"Resend API error: {response.get('error')}")
                
                num_sent += 1
                
            except Exception as e:
                if not self.fail_silently:
                    raise
        
        return num_sent

