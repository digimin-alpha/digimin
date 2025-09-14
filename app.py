from flask import Flask, request
import os
import telnyx

app = Flask(__name__)

# Set your API key directly from the environment variable.
telnyx.api_key = os.environ.get("TELNYX_API_KEY")

@app.route("/")
def hello_world():
    return "Hello from your Telnyx Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Verify the webhook signature for security (optional but recommended)
        # To do this, you need to set TELNYX_PUBLIC_KEY in your environment variables.
        public_key = os.environ.get("TELNYX_PUBLIC_KEY")
        if public_key:
            telnyx.Webhook.verify_signature(
                request.data,
                request.headers.get('telnyx-signature'),
                public_key
            )
    except Exception as e:
        print(f"Webhook signature verification failed: {e}")
        # Return a 403 Forbidden response if verification fails
        return 'Webhook signature verification failed', 403

    event = request.json['data']

    if event['event_type'] == 'message.received':
        from_number = event['payload']['from']['phone_number']
        to_number = event['payload']['to'][0]['phone_number']
        message_text = event['payload']['text']

        # Log the received message for debugging
        print(f"Received message from {from_number}: {message_text}")

        try:
            # Send a reply back using the API key
            telnyx.Message.create(
                to=[from_number],
                from_=to_number,
                text=f'Hello! I received your message: "{message_text}". Thank you for reaching out!'
            )
            print("Successfully sent reply message.")
        except Exception as e:
            # This error will show up in your Render logs
            print(f"Failed to send reply: {e}")

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))

