"""
Brevo (formerly Sendinblue) email module for sending weekly newsletters.
Provides a simple interface for sending HTML emails via Brevo API.
"""
import os
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


class MailerError(Exception):
    """Raised when email sending fails."""
    pass


def get_brevo_client():
    """
    Get configured Brevo API client.
    
    Returns:
        sib_api_v3_sdk.TransactionalEmailsApi: Configured client instance
        
    Raises:
        MailerError: If BREVO_API_KEY is not configured
    """
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise MailerError("BREVO_API_KEY not configured")
    
    # Configure API key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    
    # Create API client
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    return api_instance


def send_email(to_email: str, subject: str, html_body: str, from_email: str = None, from_name: str = None) -> dict:
    """
    Send an HTML email via Brevo.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content of the email
        from_email: Sender email (defaults to BREVO_FROM_EMAIL env var)
        from_name: Sender name (defaults to BREVO_FROM_NAME env var or "Quantum Investor Digest")
        
    Returns:
        dict: Response with status and message
        
    Raises:
        MailerError: If sending fails
    """
    # Get sender email from env or use provided
    if not from_email:
        from_email = os.environ.get('BREVO_FROM_EMAIL')
        if not from_email:
            raise MailerError("BREVO_FROM_EMAIL not configured and no from_email provided")
    
    # Get sender name
    if not from_name:
        from_name = os.environ.get('BREVO_FROM_NAME', 'Quantum Investor Digest')
    
    try:
        # Get API client
        api_instance = get_brevo_client()
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": from_name, "email": from_email},
            subject=subject,
            html_content=html_body
        )
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        logging.info(f"Email sent to {to_email}, message_id: {api_response.message_id}")
        
        return {
            "status": "sent",
            "message_id": api_response.message_id,
            "message": f"Email sent successfully to {to_email}"
        }
        
    except ApiException as e:
        logging.error(f"Brevo API exception for {to_email}: {str(e)}")
        raise MailerError(f"Failed to send email: {str(e)}")
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        raise MailerError(f"Failed to send email: {str(e)}")


def send_bulk_email(recipients: list, subject: str, html_body: str, from_email: str = None, from_name: str = None) -> dict:
    """
    Send the same email to multiple recipients (one by one via transactional API).
    
    Args:
        recipients: List of email addresses
        subject: Email subject line
        html_body: HTML content of the email
        from_email: Sender email (defaults to BREVO_FROM_EMAIL env var)
        from_name: Sender name (defaults to BREVO_FROM_NAME env var)
        
    Returns:
        dict: Summary of sent/failed emails
    """
    sent = []
    failed = []
    
    for recipient in recipients:
        try:
            send_email(recipient, subject, html_body, from_email, from_name)
            sent.append(recipient)
        except MailerError as e:
            logging.error(f"Failed to send to {recipient}: {str(e)}")
            failed.append({"email": recipient, "error": str(e)})
    
    return {
        "total": len(recipients),
        "sent": len(sent),
        "failed": len(failed),
        "failed_emails": failed
    }
