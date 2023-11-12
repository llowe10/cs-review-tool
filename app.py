# from server_class import Server
from flask import Flask, jsonify, request, render_template, redirect, url_for

GAME_SERVER_HOST = '127.0.0.1'
GAME_SERVER_PORT = 1891

# Creating the Web Application
app = Flask(__name__)
# serve = Server('127.0.0.1', 1891)

# Application homepage
@app.route("/")
def home():
    return render_template("home.html")

# Check if chain is valid in Application
@app.route("/test", methods=["GET"])
def test():
    response = {
        "message": "Testing app.",
        "tester": "llowe10"
    }
    # return render_template("status_message.html", message=response), 200
    return jsonify(response), 200

# Running the app
app.run(host="127.0.0.1", port=5000, debug=True)