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

# This block ensures the application runs only when the script is executed directly,
# not when it's imported as a module. This is important for deployment services like Render.
if __name__ == '__main__':
    # The debug=True flag allows for automatic reloading on code changes,
    # which is helpful during local development. For production, it's often set to False.
    app.run(debug=True)
