# Web3 is a python API for interacting with the Etherium Blockchain
from web3 import Web3
# Random is neccessary for generating pseudorandom integers
import random
# Time is neccessary for making timers
import time

## Connect to Ganache Local Blockchain
ganache_url = "http://127.0.0.1:7545" # URL of ganache session
w3 = Web3(Web3.HTTPProvider(ganache_url)) # Web3 session token for ganache 

## Checks connection to Ganache environment
if w3.is_connected():
    print("✅ Connected to Ganache")
else:
    print("❌ Failed to connect")

## Select an account (needs to be secured)
User = input("Please select an account 1, 2, or 3 :") 
if User == '1':
    contract_address = ""  # Address of deployment 1
if User == '2':
    contract_address = ""  # Address of deployment 2
if User == '3':
    contract_address = ""  # Address of deployment 3  


## Set Up Smart Contract Details
#JSON data to help python understand Solidity
contract_abi = [
	{
		"inputs": [],
		"name": "deleteNumber",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_number",
				"type": "uint256"
			}
		],
		"name": "setNumber",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getNumber",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "storedNumber",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}

]

## Load the contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

guess = False
while guess != True:

	## Generate the random number
	number = random.randint(0, 999999)  # Includes values from 000000 to 999999
	otp = int(str(number).zfill(6))  # Ensures it's always 6 digits

	## Send Transaction (Requires Private Key)
	private_key = "0x43280d200e2182d6eb15d3862e635da00d36665816068b60fc36ed268bf1dd8f"  # Ganache Account private key
	account = w3.eth.account.from_key(private_key) # Gets account information
	nonce = w3.eth.get_transaction_count(account.address) 

	## Builds the transaction ID to verify the interraction with Ethereum
	tx = contract.functions.setNumber(otp).build_transaction({
		'chainId': 1337,  # Chain ID for Ganache
		'gas': 200000, # Gas limit
		'gasPrice': w3.to_wei('10', 'gwei'), # Gas price calculated from session data
		'nonce': nonce # Nonce to ensure no duplicate transmissions
	})

	## Sign and send the transaction
	signed_tx = w3.eth.account.sign_transaction(tx, private_key) # Assigns the transaction to current account
	tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # Creates a hash of the data before sending
	print(f"Transaction sent: {w3.to_hex(tx_hash)}") # Returns to user

	## Call Read Function (No Gas Required)
	stored_number = contract.functions.getNumber().call() # Sets stored_number to the number in the user location in memory which *should* be the same as the generated one
	print(f"Stored Number: {stored_number}")
     
	attempt = input("What number do you see on screen?")
    
	if attempt == str(stored_number):
		print("Correct! Well done")
		guess = True
          
	else:
		print("Incorrect :( )")

	## Delete the number after 30 seconds to save on gas money and for security
	time.sleep(10) # 5 second timer is only for debugging purposes


