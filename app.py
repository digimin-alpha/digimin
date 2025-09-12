#from flask import Flask
#app = Flask(__name__)

#@app.route('/webhook') 
#def hello_world():
 #   return 'Hello, World!'
from flask import Flask

# Create the Flask application instance.
app = Flask(__name__)

# Define the route for the webhook endpoint.
# The URL path is '/webhook'.
@app.route('/webhook')
def hello_world():
    """
    This function handles requests to the /webhook endpoint.
    It returns a simple string "Hello, World!".
    """
    return 'Hello, World!'

# This block ensures the application runs only when the script is executed directly.
if __name__ == '__main__':
    # Run the app and set its "public street address" to 0.0.0.0,
    # so that the Render service can connect to it.
    app.run(host='0.0.0.0', port=5000)
