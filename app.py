import socket
from client_app import Client
from flask import Flask, jsonify, request, render_template, redirect, url_for

GAME_SERVER_HOST = '127.0.0.1'
GAME_SERVER_PORT = 1891
clients = []

# Creating the Web Application
app = Flask(__name__)

# Application homepage
@app.route("/")
def home():
    return render_template("home.html")

# Test method
@app.route("/test", methods=["GET"])
def test():
    response = {
        "message": "Testing app.",
        "tester": "llowe10"
    }
    # return render_template("status_message.html", message=response), 200
    return jsonify(response), 200

# Start game client
@app.route("/start", methods=["GET"])
def start():
    client = Client()
    client.start_client(GAME_SERVER_HOST, GAME_SERVER_PORT)
    client.set_username()
    clients.append(client)

    response = {
        "message": "Successfully started game client.",
        "clients": f"{clients}",
        "tester": "llowe10"
    }

    # return render_template("status_message.html", message=response), 200
    return jsonify(response), 200

# Running the app
app.run(host="127.0.0.1", port=5000, debug=True)