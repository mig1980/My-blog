"""
Brevo (formerly Sendinblue) email module for sending weekly newsletters.
Provides a simple interface for sending HTML emails via Brevo API.
"""
import os
import logging
import time
from typing import Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0):
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay on each retry (default: 2.0)
    
    Returns:
        Decorator function that wraps the target function with retry logic
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (ApiException, ConnectionError, TimeoutError) as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        # Check if error is retryable (5xx or network errors)
                        is_retryable = False
                        if isinstance(e, ApiException):
                            status = getattr(e, 'status', 0)
                            is_retryable = status >= 500 or status == 429  # Server errors or rate limit
                        else:
                            is_retryable = True  # Network errors are always retryable
                        
                        if is_retryable:
                            logging.warning(
                                f"Retryable error on attempt {attempt + 1}/{max_retries + 1}: {str(e)}. "
                                f"Retrying in {delay:.1f}s..."
                            )
                            time.sleep(delay)
                            delay *= backoff_factor
                            continue
                    
                    # Non-retryable error or max retries reached
                    raise last_exception
                except Exception as e:
                    # Non-retryable exceptions (4xx client errors, etc.)
                    raise e
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


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


@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def _send_email_with_retry(api_instance, send_smtp_email, to_email: str):
    """
    Internal function to send email with retry logic.
    Separated to allow retry decorator to work properly.
    """
    return api_instance.send_transac_email(send_smtp_email)


def send_email(to_email: str, subject: str, html_body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> dict:
    """
    Send an HTML email via Brevo with automatic retry on transient failures.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content of the email
        from_email: Sender email (defaults to BREVO_FROM_EMAIL env var)
        from_name: Sender name (defaults to BREVO_FROM_NAME env var or "Quantum Investor Digest")
        
    Returns:
        dict: Response with status and message
        
    Raises:
        MailerError: If sending fails after all retries
    """
    # Get sender email from env or use provided
    if not from_email:
        from_email = os.environ.get('BREVO_FROM_EMAIL')
        if not from_email:
            logging.error("BREVO_FROM_EMAIL not configured")
            raise MailerError("BREVO_FROM_EMAIL not configured and no from_email provided")
    
    # Get sender name
    if not from_name:
        from_name = os.environ.get('BREVO_FROM_NAME', 'Quantum Investor Digest')
    
    try:
        # Get API client (may raise MailerError)
        api_instance = get_brevo_client()
        
        # Create email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": from_name, "email": from_email},
            subject=subject,
            html_content=html_body
        )
        
        # Send email with retry logic
        api_response = _send_email_with_retry(api_instance, send_smtp_email, to_email)
        
        logging.info(
            f"Email sent successfully to {to_email}, message_id: {api_response.message_id}, "
            f"subject: '{subject[:50]}...'"
        )
        
        return {
            "status": "sent",
            "message_id": api_response.message_id,
            "message": f"Email sent successfully to {to_email}"
        }
        
    except MailerError:
        # Re-raise configuration errors from get_brevo_client()
        logging.error(f"Configuration error for {to_email}: BREVO_FROM_EMAIL not set")
        raise
    except ApiException as e:
        status = getattr(e, 'status', 'unknown')
        logging.error(
            f"Brevo API exception for {to_email}: status={status}, error={str(e)}",
            extra={'recipient': to_email, 'api_status': status}
        )
        raise MailerError(f"Brevo API error (status {status}): {str(e)}")
    except Exception as e:
        logging.error(
            f"Unexpected error sending to {to_email}: {type(e).__name__}: {str(e)}",
            extra={'recipient': to_email, 'error_type': type(e).__name__}
        )
        raise MailerError(f"Unexpected error: {str(e)}")


def send_bulk_email(recipients: list, subject: str, html_body: str, from_email: Optional[str] = None, from_name: Optional[str] = None) -> dict:
    """
    Send the same email to multiple recipients (one by one via transactional API).
    Includes retry logic for each recipient and detailed progress logging.
    
    Args:
        recipients: List of email addresses
        subject: Email subject line
        html_body: HTML content of the email
        from_email: Sender email (defaults to BREVO_FROM_EMAIL env var)
        from_name: Sender name (defaults to BREVO_FROM_NAME env var)
        
    Returns:
        dict: Summary of sent/failed emails with detailed failure information
    """
    sent = []
    failed = []
    total = len(recipients)
    
    logging.info(f"Starting bulk email send: {total} recipients, subject: '{subject[:50]}...'")
    
    for idx, recipient in enumerate(recipients, 1):
        try:
            send_email(recipient, subject, html_body, from_email, from_name)
            sent.append(recipient)
            
            # Log progress every 10 emails or at completion
            if idx % 10 == 0 or idx == total:
                logging.info(f"Bulk send progress: {idx}/{total} processed, {len(sent)} sent, {len(failed)} failed")
                
        except MailerError as e:
            error_msg = str(e)
            logging.error(
                f"Failed to send to {recipient} ({idx}/{total}): {error_msg}",
                extra={'recipient': recipient, 'progress': f"{idx}/{total}"}
            )
            failed.append({"email": recipient, "error": error_msg})
    
    result = {
        "total": total,
        "sent": len(sent),
        "failed": len(failed),
        "failed_emails": failed
    }
    
    logging.info(
        f"Bulk email send completed: {len(sent)}/{total} sent successfully, {len(failed)} failed",
        extra=result
    )
    
    return result
