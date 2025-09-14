import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telnyx.webhook import Webhook

# Load environment variables from the .env file.
# This works for local development. On Render, the variables are provided directly.
load_dotenv()

# Set up Telnyx API client using the API key from your environment.
try:
    import telnyx
    telnyx.api_key = os.getenv("TELNYX_API_KEY")
except ImportError:
    print("Telnyx Python SDK not found. Please install it using `pip install telnyx`.")
    telnyx = None

# Load API keys and numbers from environment variables.
TELNYX_NUMBER = os.getenv("TELNYX_NUMBER")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
# This is the new key for webhook verification. You must get it from the Telnyx Portal
# and set it as an environment variable in Render.
TELNYX_PUBLIC_KEY = os.getenv("TELNYX_PUBLIC_KEY")

# OpenRouter API endpoint.
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Create the Flask application instance.
app = Flask(__name__)

def get_openrouter_response(message_content):
    """
    Makes a POST request to the OpenRouter API to get a chat completion response.
    
    Args:
        message_content (str): The user's message to send to the AI.
        
    Returns:
        str: The AI's response text, or an error message if the request fails.
    """
    if not OPENROUTER_API_KEY or not OPENROUTER_MODEL:
        return "Sorry, the AI is not configured correctly."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # The X-Title header is optional but good practice for analytics.
        "X-Title": "Telnyx SMS Bot"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": message_content}
        ]
    }
    
    try:
        print(f"Sending message to OpenRouter model: {OPENROUTER_MODEL}")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
        
        response_data = response.json()
        
        # Extract the AI's response from the JSON payload.
        if "choices" in response_data and response_data["choices"]:
            return response_data["choices"][0]["message"]["content"]
        else:
            return "Sorry, the AI did not provide a response."

    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return "Sorry, I'm having trouble connecting to the AI right now."
    except json.JSONDecodeError as e:
        print(f"Error decoding OpenRouter response: {e}")
        return "There was an error processing the AI's response."

# Add a simple root route for basic health checks.
@app.route('/', methods=['GET'])
def index():
    return "Hello! Your Flask app is running. This is not the webhook endpoint."

@app.route('/webhook', methods=['POST'])
def handle_telnyx_webhook():
    """
    Handles incoming messages from Telnyx via a webhook POST request.
    This function processes the inbound message and sends a response.
    """
    # 1. Verify the request signature for security.
    # We now use the built-in Telnyx SDK function for this.
    telnyx_signature = request.headers.get("telnyx-signature")

    if not telnyx_signature or not TELNYX_PUBLIC_KEY:
        print("Missing Telnyx-Signature header or public key. Skipping verification.")
    else:
        try:
            # This method will raise a ValueError if the signature is invalid.
            Webhook.verify_signature(request.data, telnyx_signature, TELNYX_PUBLIC_KEY)
            print("Webhook signature verified successfully.")
        except ValueError as e:
            print(f"Webhook signature verification failed: {e}")
            return jsonify({"status": "error", "message": "Invalid webhook signature"}), 401

    if not telnyx:
        print("Telnyx SDK is not available. Cannot handle webhook.")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    try:
        # The webhook payload from Telnyx is in the request body.
        payload = request.json["data"]["payload"]
        
        # Check if this is an inbound message.
        if payload.get("direction") == "inbound":
            from_number = payload["from"]["phone_number"]
            message_content = payload["text"]
            
            print(f"Received inbound message from {from_number}: {message_content}")

            # Get a response from the OpenRouter AI.
            ai_response = get_openrouter_response(message_content)

            # Send the AI's response back to the user via Telnyx.
            try:
                telnyx.Message.create(
                    from_=TELNYX_NUMBER,
                    to=from_number,
                    text=ai_response
                    )

                )
                print(f"Successfully sent response to {from_number}")
            except Exception as e:
                print(f"Error sending message with Telnyx: {e}")
    
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Invalid webhook payload. Error: {e}")
        # Return a 200 OK even on error to prevent Telnyx from retrying.
    
    # Always return a 200 OK to acknowledge receipt of the webhook.
    return jsonify({"status": "success", "message": "Webhook received successfully"}), 200

# This block ensures the application runs only when the script is executed directly.
if __name__ == '__main__':
    # Use the PORT environment variable provided by Render.com
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
