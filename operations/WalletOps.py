#!/usr/bin/env python3

import json
import base64
from flask_socketio import send, emit
from algosdk import account, mnemonic, constants
from algosdk.v2client import algod
from algosdk.future import transaction

bouygues = {
"public_address" : "H4CVM6GSHGVKPBY6TMBTD3QTG6HALYBAUUOTB4NVIKQV745A36XBLXXGRA",
"private_key" : "jsqiOW4PAnHnu1e2Wa+IKW9xBUAKz9cnsKokdceKKgM/BVZ40jmqp4cemwMx7hM3jgXgIKUdMPG1QqFf86Dfrg=="
}

def get_algod_client():
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_address = "http://localhost:4001"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    return algod_client

def create_wallet():
    secret_key, my_address = account.generate_account()
    m = mnemonic.from_private_key(secret_key)
    print("My address: {}".format(my_address))
    print("My private key: {}".format(secret_key))
    print("My passphrase: {}".format(m))
    return (my_address, secret_key)

def make_transaction(user, dest, amount):
    print("User type: ".format(type(user)))
    print(type(dest))
    algod_client = get_algod_client()
    # ------------- DEFINE THE TRANSACTION ---------------------
    params = algod_client.suggested_params()    # Sets the client what will do the transaction for us (with default params)
    params.flat_fee = constants.MIN_TXN_FEE     # idem
    params.fee = 1000                           # idem
    
    # Add a personalized note to the transaction
    note = "Thank you for using Bouygues!".encode()
    # Unsigned Transaction Object defined here
    unsigned_txn = transaction.PaymentTxn(user["public_address"], params, dest["public_address"], int(amount), None, note)
    # ----------------- SIGN THE TRANSACTION WITH PRIVATE KEY ---------
    signed_txn = unsigned_txn.sign(user["private_key"])

    # ------------------ SUBMIT THE TRANSACTION --------------------
    # The following command pushes the transaction to the Node Client
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # ------------------ WAIT FOR CONFIRMATION ---------------------
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        return {"transaction" : "failed", "tokens_sent" : "0"}

    send(user["username"] + ' sent you some money.', to=dest["session_id"])

    return {"transaction": "confirmed", "tokens_sent" : str(amount)}

''' User exchanges data for tokens/points '''
def exchange_data_for_tokens(user, amount):
    algod_client = get_algod_client()
    params = algod_client.suggested_params()
    params.flat_fee = constants.MIN_TXN_FEE
    params.fee = 1000
    note = "Thank you for using Bouygues Token!".encode()
    unsigned_txn = transaction.PaymentTxn(bouygues["public_address"], params, user["public_address"], amount, None, note)
    signed_txn = unsigned_txn.sign(bouygues["private_key"])
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        return {"transaction" : "Failed", "tokens_recvd" : "0"}
    return {"transaction" : "confirmed", "tokens_recvd" : str(amount)}


def check_funding(wallet_address):
    client = get_algod_client()
    account_info = client.account_info(wallet_address)
    amount = account_info.get('amount')
    # Returns a dictionary of assets
    assets = account_info.get('assets')
    for asa in assets:
        if asa['asset-id'] == 14512352:
            amount = int(asa['amount'])
    print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")
    return {"amount": int(amount)}
