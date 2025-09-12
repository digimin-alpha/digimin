#from flask import Flask
#app = Flask(__name__)

#@app.route('/webhook') 
#def hello_world():
 #   return 'Hello, World!' 
from flask import Flask

# Create the Flask application instance.
app = Flask(__name__)

# This route handles requests to the root URL ("/").
# It's a good practice to have a default route for your application's homepage.
@app.route('/')
def index():
    """
    Returns a simple greeting to confirm the application is working.
    """
    return 'Hello, World!'

# This route is for your specific webhook endpoint.
@app.route('/webhook')
def hello_world():
    """
    Handles requests to the /webhook endpoint.
    """
    return 'Hello, World!'

# This block ensures the application runs only when the script is executed directly.
if __name__ == '__main__':
    # Run the app and set its "public street address" to 0.0.0.0,
    # so that the Render service can connect to it.
    app.run(host='0.0.0.0', port=5000)
