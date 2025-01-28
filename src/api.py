import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# @app.route('/api', methods=['POST'])

def connect_to_userDB():
    # code to connect to the user database goes here


if __name__ == '__main__':
    connect_to_userDB()
    app.run(port=3020)