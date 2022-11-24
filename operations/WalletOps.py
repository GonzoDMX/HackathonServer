#!/usr/bin/env python3

from algosdk import account, mnemonic
from algosdk.v2client import algod

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
