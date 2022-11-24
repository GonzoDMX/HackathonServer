#!/usr/bin/env python3

import sys
import json
from flask import Flask, request
from operations.WalletOps import create_wallet, check_funding

app = Flask(__name__)

''' Handle New User POST requests '''
@app.route("/create_user", methods=['POST'])
def create_user():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        # TODO check if username already exists
        # If not generate a wallet
        with open("./db.json") as file:
            string = file.read()
            obj = json.loads(string)
        
        wallet_address, private_key = create_wallet()

        for user in obj["users"]:
            if (user["username"] == body["username"]):
                print("HERE")
                return "This username is already taken."

        obj["users"].append({ "username": body["username"], "public_address": wallet_address, "private_key": private_key })

        with open("./db.json", 'w') as out_file:
            out = json.dumps(obj)
            out_file.write(out)

        print("Processing new user: {}".format(json))
        return "ok\n"
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Transaction POST requests '''
@app.route("/transaction", methods=['POST'])
def transaction():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        print("Processing transaction: {}".format(json))
        return "ok\n"
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Smart-Contract create POST requests '''
@app.route("/write_contract", methods=['POST'])
def write_contract():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        print("Writing contract: {}".format(json))
        return "ok\n"
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Smart-Contract signer POST requests '''
@app.route("/sign_contract", methods=['POST'])
def sign_contract():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        print("Signing contract: {}".format(json))
        return "ok\n"
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


if __name__ == "__main__":
    arg = sys.argv[1].lower()
    if arg == "local":
        print("Starting local server@127.0.0.1:5000...")
        app.run(host='127.0.0.1', port=5000)
    elif arg == "prod":
        print("Starting production server@0.0.0.0:80...")
        app.run(host='0.0.0.0', port=80)
    else:
        print('    Missing argument:\n' + 
              '\tlocal - for running tests\n' + 
              '\tprod  - to put server online')
