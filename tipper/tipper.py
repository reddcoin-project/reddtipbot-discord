import requests
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import json

# load configs
with open("config.json") as json_data_file:
    config = json.load(json_data_file)

# rpc configs
rpc_username = config['wallet']['user']
rpc_password = config['wallet']['password']
rpc_ip = config['wallet']['host']
rpc_port = config['wallet']['port']
txfee = config['wallet']['txfee']

con = AuthServiceProxy('http://%s:%s@%s:%i'%(rpc_username, rpc_password, rpc_ip, rpc_port))
con.settxfee(txfee)

## Tip commands ##

# validate address
def validateAddress(address):
    validate = con.validateaddress(address)
    return validate['isvalid']

# get user account's address
def getAddress(account):
    return con.getaccountaddress(account)

# get account's balance
def getBalance(account,minconf=6):
    return con.getbalance(account,minconf)

# process withdraw and transfer RDD to withdrawal address
def withdraw(account,destination,amount):
    if amount > getBalance(account) or amount <= 0:
        raise ValueError("Invalid amount.")
    elif amount == getBalance(account) or (amount + txfee) > getBalance(account):
        return con.sendfrom(account,destination,(amount - config['wallet']['txfee']))
    else:
        return con.sendfrom(account,destination,amount)

# process tip by moving RDD from sender to receiver's account
def tip(account,destination,amount):
    if amount > getBalance(account) or amount <= 0:
        raise ValueError("Invalid amount.")
    else:
        con.move(account,destination,amount)

# process rain by dividing and moving the RDD amount existing user accounts
def rain(account,amount):
    if amount > getBalance(account) or amount <= 0:
        raise ValueError("Invalid amount.")
    else:
        accounts = con.listaccounts()
        eachTip = amount / (len(accounts) - 2)
        for ac in accounts:
            if (str(ac) != account and str(ac) != ""):
                tip(account,ac,eachTip)
        return eachTip

# get all user accounts from the wallet
def getUsers():
    return con.listaccounts()

# get reddcoin stats - multiplier, block height
def getStats():
    inflationMultiplier = con.getinflationmultiplier()
    users = con
    blockHeight = inflationMultiplier['height']
    multiplier = inflationMultiplier['multiplier']
    stats = [blockHeight, multiplier]
    return stats