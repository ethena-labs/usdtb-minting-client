import json
import os
import time
import logging
from dataclasses import dataclass
from enum import IntEnum

import requests
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import to_hex, to_bytes
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] - %(message)s')

# Load environment variables
env_path = find_dotenv()
load_dotenv(env_path)

# Constants
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
USTB_MINTING_ADDRESS = "0x4a6B08f7d49a507778Af6FB7eebaE4ce108C981E" # staging contract address
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
BUIDL_ADDRESS = "0x7712c34205737192402172409a8f7ccef8aa2aec"
COLLATERAL_ASSET = "USDC"
COLLATERAL_ASSET_ADDRESS = COLLATERAL_ASSET == "USDC" and USDC_ADDRESS or BUIDL_ADDRESS, PRIVATE_KEY
AMOUNT = 25
ALLOW_INFINITE_APPROVALS = True
UINT256_MAX = 2 ** 256 - 1

# URLs
USTB_PUBLIC_URL = "https://public.api.ustb.money/"
USTB_PRIVATE_URL = "https://private.api.ustb.money/"
USTB_PUBLIC_URL_STAGING = "https://public.api.staging.ustb.money/"
USTB_PRIVATE_URL_STAGING = "https://private.api.staging.ustb.money/"

class SignatureType(IntEnum):
    EIP712 = 0
    EIP1271 = 1

@dataclass(init=True, order=True)
class Signature:
    signature_type: SignatureType
    signature_bytes: bytes

def load_abi(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

def get_rfq_data(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching RFQ data: {e}")
        return None

def big_int_amount(amount: int):
    return amount * (10 ** 6)

def get_allowance(w3, collateral_address: str, private_key: str):
    account = Account.from_key(PRIVATE_KEY)
    erc20_abi = load_abi("erc20_abi.json")
    allowance_contract = w3.eth.contract(address=Web3.to_checksum_address(collateral_address), abi=erc20_abi)

    allowance = allowance_contract.functions.allowance(account.address, USTB_MINTING_ADDRESS).call()
    return allowance

def approve(w3, collateral_address: str, private_key: str, amount: int):
    erc20_abi = load_abi("erc20_abi.json")
    contract = w3.eth.contract(address=Web3.to_checksum_address(collateral_address), abi=erc20_abi)

    transaction = contract.functions.approve(USTB_MINTING_ADDRESS, amount)

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return tx_hash.hex()

def create_mint_order(rfq_data, acc, collateral_asset_address):
    logging.info("Creating mint order...")
    return {
        "order_id": str(rfq_data["rfq_id"]),
        "order_type": "MINT",
        "expiry": int(time.time() + 60),
        "nonce": int(time.time() + 60),
        "benefactor": acc.address,
        "beneficiary": acc.address,
        "collateral_asset": collateral_asset_address,
        "collateral_amount": int(rfq_data["collateral_amount"]),
        "ustb_amount": int(rfq_data["ustb_amount"]),
    }

"""
Signs an order using the provided account and returns the signature. EIP712 signature is used.
    struct Order(
        string  order_id,
        uint8   order_type,
        uint120 expiry,
        uint128 nonce,
        address benefactor,
        address beneficiary,
        address collateral_asset,
        uint128 collateral_amount,
        uint128 ustb_amount
    )
"""
def sign_order(w3, mint_order, acc, ustb_minting_contract):
    logging.info("Signing order...")
    order_tuple = (
        str(mint_order["order_id"]),
        0 if mint_order["order_type"] == "MINT" else 1,
        mint_order["expiry"],
        mint_order["nonce"],
        w3.to_checksum_address(mint_order["benefactor"]),
        w3.to_checksum_address(mint_order["beneficiary"]),
        w3.to_checksum_address(mint_order["collateral_asset"]),
        mint_order["collateral_amount"],
        mint_order["ustb_amount"],
    )
    order_hash = ustb_minting_contract.functions.hashOrder(order_tuple).call()
    order_signed = acc.signHash(order_hash)
    order_rsv = to_bytes(order_signed.r) + to_bytes(order_signed.s) + to_bytes(order_signed.v)
    return Signature(SignatureType.EIP712, order_rsv)

def main():
    logging.info("Starting USTB minting script...")
    if not all([PRIVATE_KEY, RPC_URL]):
        logging.error("Missing environment variables. Please check your .env file.")
        return
    if not COLLATERAL_ASSET in ["USDC", "BUIDL"]:
        logging.error("Invalid COLLATERAL_ASSET.")
        return

    mint_abi = load_abi("ustb_mint_abi.json")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    allowance = get_allowance(w3, COLLATERAL_ASSET_ADDRESS, PRIVATE_KEY)
    logging.info(f"Allowance: {allowance}")

    if allowance < big_int_amount(AMOUNT):
        approval_amount = UINT256_MAX if ALLOW_INFINITE_APPROVALS else big_int_amount(AMOUNT)

        tx_hash = approve(w3, COLLATERAL_ASSET_ADDRESS, PRIVATE_KEY, approval_amount)
        print(f"Approval submitted: https://etherscan.io/tx/{tx_hash}")

    ustb_minting_contract = w3.eth.contract(address=Web3.to_checksum_address(USTB_MINTING_ADDRESS), abi=mint_abi)

    rfq_url = f"{USTB_PUBLIC_URL_STAGING}rfq?pair={COLLATERAL_ASSET}/UStb&type_=ALGO&side=MINT&size={AMOUNT}"
    rfq_data = get_rfq_data(rfq_url)

    if rfq_data is None:
        return

    acc: LocalAccount = Account.from_key(PRIVATE_KEY)
    mint_order = create_mint_order(rfq_data, acc, COLLATERAL_ASSET_ADDRESS)
    signature = sign_order(w3, mint_order, acc, ustb_minting_contract)

    signature_hex = to_hex(signature.signature_bytes)
    order_url = f"{USTB_PUBLIC_URL_STAGING}order?signature={signature_hex}"

    try:
        logging.info(f"Submitting order: {mint_order}")
        response = requests.post(order_url, json=mint_order, timeout=60)
        response_data = response.json()
        if response.status_code != 200:
            logging.error(f"Issue submitting order: HTTP {response.status_code}: {response_data['error']}")
        else:
            tx_id = response_data["tx"]
            logging.info(f"Transaction submitted: https://etherscan.io/tx/{tx_id}")
    except requests.RequestException as e:
        logging.error(f"Error submitting order: {e}")

if __name__ == "__main__":
    main()