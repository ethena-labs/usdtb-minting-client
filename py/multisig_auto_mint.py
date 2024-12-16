"""
This module provides functionality to handle JSON data.
It includes functions to read, write, and manipulate JSON objects.
"""

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
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s"
)

# Load environment variables
env_path = find_dotenv()
load_dotenv(env_path)

# Constants
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
RPC_URL = os.getenv("RPC_URL")
USDTB_MINTING_ADDRESS = (
    "0xa3DDBf92077b850E29C4805Df0a2459Ae048416a"
)
USDC_ADDRESS = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
BUIDL_ADDRESS = Web3.to_checksum_address("0x7712c34205737192402172409a8F7ccef8aA2AEc")
MULTISIG = Web3.to_checksum_address("0x915e2215F57D4373a5c94F0139b6fbDDCA4dE4CA")
COLLATERAL_ASSET = "USDC"
COLLATERAL_ASSET_ADDRESS = USDC_ADDRESS if COLLATERAL_ASSET == "USDC" else BUIDL_ADDRESS

MIN_MINT_AMOUNT = 66_000
MAX_MINT_AMOUNT = 5_000_000
ALLOW_INFINITE_APPROVALS = False

# URLs
USDTB_PUBLIC_URL = "https://public.api.usdtb.money/"
USDTB_PRIVATE_URL = "https://private.api.usdtb.money/"
USDTB_PUBLIC_URL_STAGING = "https://public.api.staging.usdtb.money/"
USDTB_PRIVATE_URL_STAGING = "https://private.api.staging.usdtb.money/"


def load_abi(file_path):
    """
    Load and return the ABI (Application Binary Interface) from a JSON file.

    Args:
        file_path (str): The path to the JSON file containing the ABI.

    Returns:
        dict: The ABI loaded from the file.
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


ERC20_ABI = load_abi("py/erc20_abi.json")


class SignatureType(IntEnum):
    """Enumeration of supported signature types for minting."""

    EIP712 = 0
    EIP1271 = 1


@dataclass(init=True, order=True)
class Signature:
    """
    Represents a digital signature with its type and corresponding bytes.

    Attributes:
        signature_type (SignatureType): The type of the signature (e.g., EIP712, EIP1271).
        signature_bytes (bytes): The raw bytes of the signature.
    """

    signature_type: SignatureType
    signature_bytes: bytes


def get_rfq_data(url):
    """
    Fetches RFQ (Request for Quote) data from the given URL.

    Args:
        url (str): The endpoint URL to fetch data from.

    Returns:
        dict or None: Parsed JSON data if the request is successful,
        or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching RFQ data: {e}")
        return None


def get_balance(w3, collateral_address: str):
    """
    Retrieves the token allowance for the multisig address.

    Args:
        w3 (Web3): The Web3 instance connected to the blockchain.
        collateral_address (str): The address of the ERC-20 token contract.

    Returns:
        int: The balance value for the multisig address.
    """
    collateral_contract = w3.eth.contract(
        address=Web3.to_checksum_address(collateral_address), abi=ERC20_ABI
    )

    balance = collateral_contract.functions.balanceOf(
        MULTISIG
    ).call()
    return balance/10**6


def create_mint_order(rfq_data, multisig, collateral_asset_address):
    """
    Creates a mint order with the provided RFQ data and account details.

    This function generates a mint order dictionary that includes the RFQ ID, order type, expiry time,
    nonce, and details about the benefactor and beneficiary. It also includes collateral information
    such as the asset address and amount, as well as the amount of USDTB to mint.

    Args:
        rfq_data (dict): A dictionary containing the RFQ data.
        acc (object): An account object that contains the address of the user making the mint request.
        collateral_asset_address (str): The address of the collateral asset to be used in the mint order.

    Returns:
        dict: A dictionary containing the mint order with the following keys:
            - order_id (str): The RFQ ID as a string.
            - order_type (str): The type of the order, which is "MINT".
            - expiry (int): The timestamp representing when the order expires.
            - nonce (int): A nonce used for order identification and security.
            - benefactor (str): The address of the benefactor (the person creating the order).
            - beneficiary (str): The address of the beneficiary (the recipient of the minted tokens).
            - collateral_asset (str): The address of the collateral asset.
            - collateral_amount (int): The amount of collateral to be provided.
            - usdtb_amount (int): The amount of USDTB to be minted.
    """
    logging.info("Creating mint order...")
    return {
        "order_id": str(rfq_data["rfq_id"]),
        "order_type": "MINT",
        "expiry": int(time.time() + 60),
        "nonce": int(time.time() + 60),
        "benefactor": multisig,
        "beneficiary": multisig,
        "collateral_asset": collateral_asset_address,
        "collateral_amount": int(rfq_data["collateral_amount"]),
        "usdtb_amount": int(rfq_data["usdtb_amount"]),
    }


def sign_order(w3, mint_order, acc, usdtb_minting_contract):
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
            uint128 usdtb_amount
        )
    """
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
        mint_order["usdtb_amount"],
    )
    order_hash = usdtb_minting_contract.functions.hashOrder(order_tuple).call()
    order_signed = acc.unsafe_sign_hash(order_hash)
    order_rsv = (
        to_bytes(order_signed.r) + to_bytes(order_signed.s) + to_bytes(order_signed.v)
    )
    return Signature(SignatureType.EIP712, order_rsv)


def main():
    """
    Minting flow
    """
    logging.info("Starting USDTB minting script...")
    if not all([PRIVATE_KEY, RPC_URL]):
        logging.error("Missing environment variables. Please check your .env file.")
        return
    if COLLATERAL_ASSET not in ["USDC", "BUIDL"]:
        logging.error("Invalid COLLATERAL_ASSET.")
        return

    mint_abi = load_abi("py/usdtb_mint_abi.json")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # pylint: disable=no-value-for-parameter
    acc: LocalAccount = Account.from_key(PRIVATE_KEY)
    usdtb_minting_contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDTB_MINTING_ADDRESS), abi=mint_abi
    )

    while True:
        balance = get_balance(w3, COLLATERAL_ASSET_ADDRESS)
        print("BALANCE", balance)
        if balance < MIN_MINT_AMOUNT:
            time.sleep(10)
            continue
        mint_amount = min(MAX_MINT_AMOUNT, balance)
        rfq_url = f"{USDTB_PUBLIC_URL}rfq?pair={COLLATERAL_ASSET}/USDtb&type_=ALGO&side=MINT&size={mint_amount}&benefactor={MULTISIG}"
        rfq_data = get_rfq_data(rfq_url)

        if rfq_data is None:
            return

        mint_order = create_mint_order(rfq_data, MULTISIG, COLLATERAL_ASSET_ADDRESS)
        signature = sign_order(w3, mint_order, acc, usdtb_minting_contract)

        signature_hex = to_hex(signature.signature_bytes)
        order_url = f"{USDTB_PUBLIC_URL}order?signature={signature_hex}"

        try:
            logging.info(f"Submitting order: {mint_order}")
            response = requests.post(order_url, json=mint_order, timeout=60)
            response_data = response.json()
            if response.status_code != 200:
                logging.error(
                    f"Issue submitting order: HTTP {response.status_code}: {response_data['error']}"
                )
            else:
                tx_id = response_data["tx"]
                logging.info(f"Transaction submitted: https://etherscan.io/tx/{tx_id}")
        except requests.RequestException as e:
            logging.error(f"Error submitting order: {e}")
        time.sleep(13)


if __name__ == "__main__":
    main()
