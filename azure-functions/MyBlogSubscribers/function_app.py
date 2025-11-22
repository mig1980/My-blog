import json
import logging
import re

import azure.functions as func
from email_subscriber import (
    subscribe_email as subscribe_email_logic,
    SubscriptionError,
)
from weekly_job import send_weekly_newsletter

app = func.FunctionApp()

@app.route(route="SubscribeEmail", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def subscribe_email(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',  # Change to your domain in production
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    # Handle preflight OPTIONS request
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            status_code=204,
            headers=headers
        )

    # Get email from request body
    try:
        req_body = req.get_json()
        email = req_body.get('email')
    except ValueError:
        return func.HttpResponse(
            json.dumps({'message': 'Invalid request body'}),
            status_code=400,
            headers=headers
        )

    # Validate email presence
    if not email:
        return func.HttpResponse(
            json.dumps({'message': 'Email is required'}),
            status_code=400,
            headers=headers
        )

    # Validate email format
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return func.HttpResponse(
            json.dumps({'message': 'Invalid email format'}),
            status_code=400,
            headers=headers
        )

    try:
        result = subscribe_email_logic(email)
        message = result.get('message', 'Subscription processed.')

        return func.HttpResponse(
            json.dumps({'message': message}),
            status_code=200,
            headers=headers
        )

    except SubscriptionError as e:
        logging.error(f'Subscription configuration error: {str(e)}')
        return func.HttpResponse(
            json.dumps({'message': 'Service configuration error'}),
            status_code=500,
            headers=headers
        )

    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                'message': 'An error occurred. Please try again later.'
            }),
            status_code=500,
            headers=headers
        )


@app.timer_trigger(schedule="0 0 12 * * FRI", arg_name="mytimer", run_on_startup=False)
def weekly_newsletter(mytimer: func.TimerRequest) -> None:
    """
    Timer trigger function that sends weekly newsletter every Friday at 12:00 PM UTC.
    
    Schedule format: "seconds minutes hours day month dayOfWeek"
    Current: 0 0 12 * * FRI = Every Friday at 12:00 PM UTC
    
    Adjust schedule as needed:
    - "0 0 9 * * MON" = Every Monday at 9:00 AM UTC
    - "0 30 14 * * *" = Every day at 2:30 PM UTC
    """
    logging.info('Weekly newsletter timer trigger started')
    
    if mytimer.past_due:
        logging.info('Timer is past due, running now')
    
    # Send the newsletter
    result = send_weekly_newsletter()
    
    logging.info(f"Weekly newsletter completed: {result}")