#!/usr/bin/env python3

import sys
import json
from flask import Flask, request
from flask_socketio import SocketIO, send, emit
from operations.WalletOps import create_wallet, check_funding as get_funding, make_transaction, exchange_data_for_tokens
from flask_sock import Sock

app = Flask(__name__)
#socketio = SocketIO(app)

sock = Sock(app)

transaction_final = False
transaction_catch = False
transaction_ret = {}
transaction_gb = 0

''' Handle New User POST requests '''
@app.route("/create_user", methods=['POST'])
def create_user():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json

        with open("./db.json") as file:
            string = file.read()
            obj = json.loads(string)
        
        for user in obj["users"]:
            if (user["username"] == body["username"]):
                print("HERE")
                return "This username is already taken."

        wallet_address, private_key = create_wallet()

        obj["users"].append({ "username": body["username"], "public_address": wallet_address, "private_key": private_key, "session_id": "" })

        with open("./db.json", 'w') as out_file:
            out = json.dumps(obj)
            out_file.write(out)

        print("Processing new user: {}".format(json))
        return "ok\n"
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Check Funding POST requests '''
@app.route("/check_funding", methods=['POST'])
def check_funding():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        
        with open("./db.json") as file:
            string = file.read()
            obj = json.loads(string)

        user_exist = False
        requested_user = {}

        for user in obj["users"]:
            if (user["username"] == body["username"]):
                user_exist = True
                requested_user = user

        if (user_exist == False): 
            return "This user does not exist."

        return get_funding(requested_user["public_address"])
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Transaction POST requests '''
@app.route("/transaction", methods=['POST'])
def transaction():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        print("Processing transaction: {}".format(body))

        with open("./db.json") as file:
            string = file.read()
            obj = json.loads(string)

        user_exist = False
        dest_user_exist = False
        requested_user = {}
        dest_user = {}

        for user in obj["users"]:
            if (user["username"] == body["username"]):
                user_exist = True
                requested_user = user
            if (user["username"] == body["dest"]):
                dest_user_exist = True
                dest_user = user

        if (user_exist == False or dest_user_exist == False):
            return "This user does not exist."

        transaction_ret = make_transaction(requested_user, dest_user, int(body["amount"]))
        transaction_final = True
        while transaction_catch == False:
            continue
        transaction_final = False
        transaction_catch == False
        return ret
    else:
        # Handle unsupported content types
        return 'Content-type not supported.'


''' Handle Data Exchange POST requests '''
''' Example of data struct: { "username" : "user1", "amount" : "1000" }'''
@app.route("/exchange", methods=['POST'])
def exchange():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json
        print("Processing transaction: {}".format(body))

        with open("./db.json") as file:
            string = file.read()
            obj = json.loads(string)

        user_exist = False
        dest_user_exist = False
        requested_user = {}
        dest_user = {}

        for user in obj["users"]:
            if (user["username"] == body["username"]):
                user_exist = True
                requested_user = user
                print("Send: {} - Addr: {}".format(user["username"], user["public_address"]))
            if (user["username"] == body["dest"]):
                dest_user_exist = True
                dest_user = user
                print("Dest: {} - Addr: {}".format(user["username"], user["public_address"]))

        if user_exist == False or dest_user_exist == False:
            return {"transaction" : "failed", "tokens_sent" : "0", "username" : request_user["username"]}

        return make_transaction(requested_user, dest_user, int(body["amount"]))
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

    
@sock.route('/')
def handle_socket(ws):
    data = ws.receive()
    print('received message: ' + data)
    with open("./db.json") as file:
        string = file.read()
        obj = json.loads(string)

    rec_data = json.loads(data)

    user_exist = False

    # Get user credentials
    for user in obj["users"]:
        if user["username"] == rec_data["username"]:
            user_exist = True
            transaction_gb = int(rec_data["amount"])

    # If user doesn't exist abort here
    if not user_exist: 
        ws.send("This user does not exist.")
        ws.close()
        return
        
    ws.send("Connected.")
    print("Serving user: {} - With {} Gb to share".format(rec_data["username"], transaction_gb))
    while transaction_final == False:
        continue
    if transaction_ret["transaction"] == "confirmed":
        ws.send(transaction_ret["username"] + ' sent you ' + transaction_ret["tokens_sent"] + 'Bouygues Tokens.')
    else:
        ws.send('Transaction with ' + transaction_ret["username"] + 'failed.')
    transaction_catch == True
    ws.close()


if __name__ == "__main__":
    arg = sys.argv[1].lower()
    if arg == "local":
        print("Starting local server@127.0.0.1:5000...")
        #socketio.run(app, host='127.0.0.1', port=5001)
        app.run(host='127.0.0.1', port=5000)
    elif arg == "prod":
        print("Starting production server@0.0.0.0:80...")
        #socketio.run(app, host='0.0.0.0', port=50)
        app.run(host='0.0.0.0', port=80)
    else:
        print('    Missing argument:\n' + 
              '\tlocal - for running tests\n' + 
              '\tprod  - to put server online')
