from flask import Flask, request
import os
import telnyx
import json

app = Flask(__name__)

# Set your API key directly from the environment variable.
telnyx.api_key = os.environ.get("TELNYX_API_KEY")

@app.route("/")
def hello_world():
    return "Hello from your Telnyx Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # We are removing webhook signature verification to get the app working.
    # We will need to re-add this later for security.
    
    # Print the entire JSON payload to debug what Telnyx is sending
    print(f"Full webhook payload received: {json.dumps(request.json, indent=2)}")

    try:
        event = request.json['data']

        if event['event_type'] == 'message.received':
            from_number = event['payload']['from']['phone_number']
            to_number = event['payload']['to'][0]['phone_number']
            message_text = event['payload']['text']

            try:
                # Send a reply back using the API key
                telnyx.Message.create(
                    to=[from_number],
                    from_=to_number,
                    text=f'Hello! I received your message: "{message_text}". Thank you for reaching out!'
                )
            except Exception as e:
                # This will print any errors from the Telnyx API to your Render logs.
                print(f"Error sending message: {e}")

    except KeyError as e:
        print(f"Error parsing webhook payload: Missing key {e}")

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
