"""
Weekly email job - sends newsletter to all active subscribers.
Triggered every Friday at 12:00 PM UTC (adjust schedule as needed).
"""
import os
import re
import logging
import requests
from email_subscriber import get_active_subscribers, SubscriptionError
from mailer import send_bulk_email, MailerError
from azure.storage.blob import BlobServiceClient

# GitHub repository configuration
GITHUB_OWNER = "mig1980"
GITHUB_REPO = "quantuminvestor"
GITHUB_POSTS_PATH = "Posts"


def get_latest_week_number() -> int:
    """
    Auto-detect the latest week number from GitHub Posts folder.
    
    Fetches file list from GitHub API and scans for: GenAi-Managed-Stocks-Portfolio-Week-X.html
    
    Returns:
        int: Latest week number (e.g., 6)
        
    Raises:
        FileNotFoundError: If no weekly posts found or GitHub API fails
    """
    # GitHub API URL to list files in Posts directory
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_POSTS_PATH}"
    
    try:
        logging.info(f"Fetching Posts directory from GitHub: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        files_data = response.json()
        
        # Extract filenames
        filenames = [item['name'] for item in files_data if item['type'] == 'file']
        
        # Find weekly portfolio posts
        pattern = r'GenAi-Managed-Stocks-Portfolio-Week-(\d+)\.html'
        week_files = [f for f in filenames if re.match(pattern, f)]
        
        if not week_files:
            raise FileNotFoundError(
                f"No weekly portfolio posts found in GitHub {GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_POSTS_PATH}"
            )
        
        # Extract week numbers and return the highest
        week_numbers = [int(re.search(pattern, f).group(1)) for f in week_files]
        latest_week = max(week_numbers)
        
        logging.info(f"Latest week detected from GitHub: {latest_week} (found {len(week_files)} posts)")
        return latest_week
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch Posts directory from GitHub: {str(e)}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    except (KeyError, ValueError) as e:
        error_msg = f"Failed to parse GitHub API response: {str(e)}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)


def get_weekly_email_content() -> dict:
    """
    Download pre-generated newsletter HTML from Azure Blob Storage.
    
    Looks for: newsletters/week{X}.html in Blob Storage
    
    Returns:
        dict: Dictionary with 'subject' and 'html_body'
        
    Raises:
        FileNotFoundError: If newsletter HTML not found (prevents sending emails)
        ValueError: If newsletter HTML is invalid or empty
        IOError: If Blob Storage access fails
    """
    # Auto-detect latest week from GitHub Posts
    week_number = get_latest_week_number()
    
    # Get Blob Storage connection string
    connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
    if not connection_string:
        error_msg = "STORAGE_CONNECTION_STRING not configured"
        logging.error(error_msg)
        raise IOError(error_msg)
    
    blob_name = f"week{week_number}.html"
    container_name = "newsletters"
    
    try:
        # Create BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        logging.info(f"Downloading newsletter from Blob Storage: {container_name}/{blob_name}")
        
        # Check if blob exists
        if not blob_client.exists():
            error_msg = (
                f"Newsletter file not found in Azure Blob Storage\n"
                f"Container: {container_name}\n"
                f"Blob: {blob_name}\n"
                f"Action required: Generate and upload newsletter HTML for week {week_number}"
            )
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Download blob content
        download_stream = blob_client.download_blob()
        html_body = download_stream.readall().decode('utf-8')
        
        logging.info(f"Successfully downloaded newsletter from Blob Storage ({len(html_body)} bytes)")
        
    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is
        raise
    except UnicodeDecodeError as e:
        error_msg = (
            f"Newsletter file encoding error: {container_name}/{blob_name}\n"
            f"Error: {str(e)}\n"
            f"Action required: Ensure file is saved as UTF-8"
        )
        logging.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = (
            f"Failed to download newsletter from Blob Storage: {container_name}/{blob_name}\n"
            f"Error: {str(e)}\n"
            f"Action required: Check Blob Storage connection and blob existence"
        )
        logging.error(error_msg)
        raise IOError(error_msg)
    
    # Validate HTML content
    if not html_body or not html_body.strip():
        error_msg = (
            f"Newsletter file is empty: {container_name}/{blob_name}\n"
            f"Action required: Generate valid newsletter HTML content"
        )
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Basic HTML structure validation
    html_lower = html_body.lower()
    if '<html' not in html_lower or '<body' not in html_lower:
        error_msg = (
            f"Newsletter file missing required HTML structure: {container_name}/{blob_name}\n"
            f"Missing: <html> and/or <body> tags\n"
            f"Action required: Ensure newsletter is valid HTML email"
        )
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    logging.info(f"Successfully validated newsletter HTML ({len(html_body)} bytes)")
    
    subject = f"📊 Week {week_number} Portfolio Update"
    
    return {
        "subject": subject,
        "html_body": html_body
    }


def send_weekly_newsletter() -> dict:
    """
    Main function to send weekly newsletter to all active subscribers.
    
    Returns:
        dict: Summary of email sending results
    """
    try:
        # Get all active subscribers
        subscribers = get_active_subscribers()
        
        if not subscribers:
            logging.info("No active subscribers found")
            return {
                "status": "completed",
                "message": "No active subscribers",
                "total": 0,
                "sent": 0,
                "failed": 0
            }
        
        logging.info(f"Found {len(subscribers)} active subscribers")
        
        # Get email content
        email_content = get_weekly_email_content()
        
        # Send to all subscribers
        result = send_bulk_email(
            recipients=subscribers,
            subject=email_content["subject"],
            html_body=email_content["html_body"]
        )
        
        logging.info(f"Weekly newsletter sent: {result['sent']}/{result['total']} successful")
        
        return {
            "status": "completed",
            "message": f"Newsletter sent to {result['sent']} subscribers",
            **result
        }
        
    except FileNotFoundError as e:
        logging.error(f"Newsletter file error: {str(e)}")
        return {
            "status": "error",
            "error_type": "missing_newsletter",
            "message": str(e),
            "total": 0,
            "sent": 0,
            "failed": 0
        }
    except ValueError as e:
        logging.error(f"Newsletter validation error: {str(e)}")
        return {
            "status": "error",
            "error_type": "invalid_newsletter",
            "message": str(e),
            "total": 0,
            "sent": 0,
            "failed": 0
        }
    except IOError as e:
        logging.error(f"Newsletter file access error: {str(e)}")
        return {
            "status": "error",
            "error_type": "file_access_error",
            "message": str(e),
            "total": 0,
            "sent": 0,
            "failed": 0
        }
    except SubscriptionError as e:
        logging.error(f"Subscription error: {str(e)}")
        return {
            "status": "error",
            "error_type": "subscription_error",
            "message": f"Failed to get subscribers: {str(e)}",
            "total": 0,
            "sent": 0,
            "failed": 0
        }
    except MailerError as e:
        logging.error(f"Mailer error: {str(e)}")
        return {
            "status": "error",
            "error_type": "mailer_error",
            "message": f"Failed to send emails: {str(e)}",
            "total": 0,
            "sent": 0,
            "failed": 0
        }
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error_type": "unexpected_error",
            "message": f"Unexpected error: {str(e)}",
            "total": 0,
            "sent": 0,
            "failed": 0
        }
