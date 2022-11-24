#!/usr/bin/env python3

import json
import base64
from algosdk import account, mnemonic, constants
from algosdk.v2client import algod
from algosdk.future import transaction

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

def make_transaction(user, dest_address):
    algod_client = get_algod_client()
    # ------------- DEFINE THE TRANSACTION ---------------------
    params = algod_client.suggested_params()    # Sets the client what will do the transaction for us (with default params)
    params.flat_fee = constants.MIN_TXN_FEE     # idem
    params.fee = 1000                           # idem
    
    # Set the amount for the transaction, in MicroAlgos 1000000 = 1 Algo
    amount = 100000
    
    # Add a personalized note to the transaction
    note = "Thank you for using Bouygues!".encode()
    
    # Unsigned Transaction Object defined here
    unsigned_txn = transaction.PaymentTxn(user["public_address"], params, dest_address, amount, None, note)
    # ---------------------------------------------------------
    
    # ----------------- SIGN THE TRANSACTION WITH PRIVATE KEY ---------
    signed_txn = unsigned_txn.sign(user["private_key"])
    # -----------------------------------------------------------------

    # ------------------ SUBMIT THE TRANSACTION --------------------
    # The following command pushes the transaction to the Node Client
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))
    # --------------------------------------------------------------


    # ------------------ WAIT FOR CONFIRMATION ---------------------
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)  
    except Exception as err:
        print(err)
        return
    # --------------------------------------------------------------


    # ----------------- PRINT FINALIZED TRANSACTION INFO -----------
    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))

    print("Starting Account balance: {} microAlgos".format(account_info.get('amount')) )
    print("Amount transfered: {} microAlgos".format(amount) )    
    print("Fee: {} microAlgos".format(params.fee) ) 
    # --------------------------------------------------------------

    account_info = algod_client.account_info(user["public_address"])
    print("Final Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")

    return {"transaction": confirmed_txn}

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
