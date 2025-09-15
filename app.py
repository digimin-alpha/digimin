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
    # This log confirms the function is being entered.
    print("Webhook function entered.")
    
    try:
        # Print the entire JSON payload to see what Telnyx is sending.
        print(f"Received JSON payload: {request.json}")
        
        event = request.json['data']

        if event['event_type'] == 'message.received':
            from_number = event['payload']['from']['phone_number']
            to_number = event['payload']['to'][0]['phone_number']
            message_text = event['payload']['text']

            # Log the received message for debugging
            print(f"Received message from {from_number}: {message_text}")
            
            # This new log will show you the numbers being used in the API call,
            # even if an error occurs.
            print(f"Attempting to send reply from {to_number} to {from_number}")

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
        else:
            print(f"Received a non-message event: {event['event_type']}")
    except Exception as e:
        print(f"Error processing webhook: {e}")

    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
