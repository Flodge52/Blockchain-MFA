from web3 import Web3
from solcx import compile_standard, install_solc
import json
import time
import threading
import random

# User selects whether to register or log in
verified = False

while verified == False:  # Loop until the user successfully logs in
    register_or_login = input("Would you like to register [1] or login [2]? ")

    if register_or_login == "1":  # Register a new user
        while verified == False:  # Loop until a valid username is provided
            # Get user input for account registration
            username = input("Please provide a username: ")
            password = input("Please provide a password: ")

            # Store username and password as a tuple
            registration = (username, password)

            # Read existing users
            try:
                with open("Database.txt", "r") as f:
                    existing_users = f.readlines() # Loops through every user entry
            except FileNotFoundError:
                existing_users = []  # If file doesn't exist, start fresh

            # Check if username already exists
            user_exists = any(username in eval(acc.strip())[0] for acc in existing_users) # Turns each entry into a tuple

            if user_exists:
                print("User already exists. Please choose a different username")
                continue

            else:
                # Append new user to the file
                with open("Database.txt", "a") as f:
                    f.write(str(registration) + '\n')
                print("Registration successful! You may now log in.")
                username = input("Enter your username: ")
                password = input("Enter your password: ")

                # Read from file and verify credentials
                try:
                    with open("Database.txt", "r") as f:
                        accounts = f.readlines()
                except FileNotFoundError:
                    accounts = []  # If file doesn't exist, no users are registered

                # Convert stored strings back to tuples and check if user exists
                accounts = [eval(acc.strip()) for acc in accounts]  # Convert string to tuple

                # Checks if the username and password tuple exists
                if (username, password) in accounts:
                    print(f"Login successful! Welcome, {username}")
                    verified = True  # Exit loop
                else:
                    print("Login failed! Incorrect username or password. Registration revoked")
                    with open("Database.txt", "r") as f:
                        lines = f.readlines()  # Read all lines into a list
                    lines.pop() # Remove the last entry from the list
                    # Write the updated content back to the file
                    with open("Database.txt", "w") as f:
                        f.writelines(lines)
                
    elif register_or_login == "2":  # Login existing user
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # Read from file and verify credentials
        try:
            with open("Database.txt", "r") as f:
                accounts = f.readlines()
        except FileNotFoundError:
            accounts = []  # If file doesn't exist, no users are registered

        # Convert stored strings back to tuples and check if user exists
        accounts = [eval(acc.strip()) for acc in accounts]  # Convert string to tuple

        if (username, password) in accounts:
            print(f"Login successful! Welcome, {username}")
            verified = True  # Exit loop
        else:
            print("Login failed! Incorrect username or password.")
    else:
        print("Invalid selection! Please choose 1 or 2.")
     

## Connect to Ethereum Network (Ganache)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545")) # Ganache localhost URL

if w3.is_connected():
    print("✅ Connected to Ethereum (Ganache)")
else:
    print("❌ Connection failed")

## Load Solidity Contract Source Code
solidity_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract UserAccount {
    address public owner;
    uint256 public accountNumber;
    uint256 public storedNumber;

    function setNumber(uint256 _number) public {
        storedNumber = _number;
    }

    function getNumber() public view returns (uint256) {
        return storedNumber;
    }

    function deleteNumber() public {
        storedNumber = 0;
    } 
    

    constructor(uint256 _accountNumber) {
        owner = msg.sender;
        accountNumber = _accountNumber;
        storedNumber = 123456;
    }
}
'''

# Compile Solidity Code
install_solc("0.8.18")  # Ensure Solidity compiler is installed

# Sets the parameters to compile the solidity code with
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"UserAccount.sol": {"content": solidity_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode.object"]
                }
            }
        },
    },
    solc_version="0.8.18", # Make sure the version matches the Pragma identifier
)

# Extract ABI and Bytecode
abi = compiled_sol["contracts"]["UserAccount.sol"]["UserAccount"]["abi"] # ABI is JSON code 
bytecode = compiled_sol["contracts"]["UserAccount.sol"]["UserAccount"]["evm"]["bytecode"]["object"] # Extracts the bytecode from the Ethereum VM

print("✅ Solidity contract compiled successfully!")

# Check against UserAccount_address.txt if a person with {username} already has a registered address
contract_address = None  # Default to None
try:
    with open("UserAccount_address.txt", "r") as f:
        for line in f:
            stored_username, stored_address = line.strip().split(" ") # Splits each line at the space to create the tuple
            if stored_username == username:
                contract_address = stored_address  # Retrieve existing contract address
                print(f"✅ Existing user found. Using stored contract address: {contract_address}")
                break  # Stop searching since we found the user
except FileNotFoundError:
    print("No contract database found. Creating a new one...")

# Set Up Account for Deployment (Ganache)
private_key = "0x411a2a9d106136540cd80ef4a95135421d1c9753b0c2c2e29ee1082a1edef8dc"  # Ganache account private key for secure transfer
account = w3.eth.account.from_key(private_key) # Gets the account information from the private key
nonce = w3.eth.get_transaction_count(account.address) # Generates a nonce so that this is only performed once

if contract_address == None: # If they actually don't have an account
    
    # Deploy Contract to account with ID 1001
    UserAccount = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = UserAccount.constructor(1001).build_transaction({
        "from": account.address,
        "gas": 2000000,
        "gasPrice": w3.to_wei("10", "gwei"),
        "nonce": nonce,
        "chainId": 1337  # Ganache chain ID
    })

    # Sign and Send Deployment Transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    # Wait for Transaction Confirmation
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Get Contract Address and Print It
    contract_address = tx_receipt.contractAddress # Gets the unique address from the deployment and saves as contract_address
    print(f"✅ Contract Deployed Successfully at: {contract_address}")

    # Save ABI & Contract Address for Future Interactions
    with open("UserAccount_abi.json", "w") as abi_file:
        json.dump(abi, abi_file)

    # Save contract address information as "[username]' '[contact_address]\n"
    with open("UserAccount_address.txt", "a") as f:
        f.write(username + " " + str(contract_address) + '\n')

    print("Address saved for future use!")

time.sleep(1)

# Load the contract
contract = w3.eth.contract(address=contract_address, abi=abi)

# Finds the address of the owner of the contract and the address of the user to ensure it is sending OTP to the correct address 
contract_owner = contract.functions.owner().call()
print(f"Contract Owner: {contract_owner}")
print(f"Your Address: {account.address}")

if contract_owner.lower() != account.address.lower(): # If owner and user have different addresses
    print("❌ ERROR: You are not the contract owner. Transaction denied.")
    exit()

# Prepares the error message if time to submit OTP runs out
def timeout():
    print("Times up buttercup'\n'")
    guess = 000000 # Fails the guess

# While loop until they get the OTP right
guess_correct = False
while guess_correct == False:

    timer = threading.Timer(10, timeout) # 10s non intrusive timer
    
    # Generate the OTP (6-digit number)
    number = random.randint(0, 999999)
    otp = int(str(number).zfill(6))  # Always ensures 6 digits

    time.sleep(1) # Sleep to give the network time to register the transaction

    # Set OTP in blockchain
    tx = contract.functions.setNumber(otp).build_transaction({
        'from': account.address,
        'chainId': 1337,
        'gas': 5000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(account.address)
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key) # Signs the transaction with PKI
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) # Sends the data to blockchain
    w3.eth.wait_for_transaction_receipt(tx_hash) # Waits for blockchain to acknowledge the tx before continuing

    #time.sleep(1)

    # Read Back the OTP
    stored_number = contract.functions.getNumber().call()
    print(f"Your OTP is: {stored_number}")

    timer.start() # Start the threaded timer

    ## User has 10 seconds to input the number correctly
    guess = input("Please enter the number that appears on-screen: ")
    if guess == str(stored_number):
        print("Correct, please proceed...")
        guess_correct = True
    else:
        print("Icorrect, please try again")

    timer.cancel()

# Delete the OTP Securely
tx_delete = contract.functions.deleteNumber().transact({'from': account.address})
w3.eth.wait_for_transaction_receipt(tx_delete)
print("OTP deleted from ledger.")

# Read Again
stored_number = contract.functions.getNumber().call()
print(f"Stored Number After Deletion: {stored_number}")  # Should be 0