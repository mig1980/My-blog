"""
Weekly email job - sends newsletter to all active subscribers.
Triggered every Friday at 12:00 PM UTC (adjust schedule as needed).
"""
import logging
from email_subscriber import get_active_subscribers, SubscriptionError
from mailer import send_bulk_email, MailerError


def get_weekly_email_content() -> dict:
    """
    Generate the weekly email content.
    
    TODO: Replace this with your actual email template or dynamic content.
    You can pull from a file, database, or generate based on your blog posts.
    
    Returns:
        dict: Dictionary with 'subject' and 'html_body'
    """
    subject = "Quantum Investor Digest - Weekly Update"
    
    # Simple HTML template - replace with your actual content
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 30px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            a { color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Quantum Investor Digest</h1>
                <p>Your Weekly AI & Investing Update</p>
            </div>
            <div class="content">
                <h2>This Week's Highlights</h2>
                <p>Welcome to your weekly digest! Here's what happened this week in AI and investing...</p>
                
                <h3>📊 Portfolio Update</h3>
                <p>Our AI-managed portfolio performance and latest trades.</p>
                
                <h3>🤖 AI Insights</h3>
                <p>Latest developments in generative AI and market analysis.</p>
                
                <h3>📰 Top Stories</h3>
                <ul>
                    <li>Story 1 placeholder</li>
                    <li>Story 2 placeholder</li>
                    <li>Story 3 placeholder</li>
                </ul>
                
                <p style="margin-top: 30px;">
                    <a href="https://quantuminvestor.net" 
                       style="background: #667eea; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Read Full Blog Post
                    </a>
                </p>
            </div>
            <div class="footer">
                <p>You're receiving this because you subscribed to Quantum Investor Digest</p>
                <p>
                    <a href="https://quantuminvestor.net">Visit Website</a> | 
                    <a href="#">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
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
        
    except SubscriptionError as e:
        logging.error(f"Subscription error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to get subscribers: {str(e)}"
        }
    except MailerError as e:
        logging.error(f"Mailer error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to send emails: {str(e)}"
        }
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
