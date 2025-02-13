import os
import time
import logging
import requests
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import to_hex, to_bytes
from web3 import Web3

from usdtb_mint_script import create_mint_order, create_redeem_order, sign_order, USDTB_PUBLIC_URL, USDC_ADDRESS \
    , BUIDL_ADDRESS, USDTB_MINTING_ADDRESS, load_abi, ERC20_ABI, get_rfq_data, USDTB_ADDRESS

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
MULTISIG = Web3.to_checksum_address(os.getenv("MULTISIG_ADDRESS"))
COLLATERAL_ASSET = "USDC"
COLLATERAL_ASSET_ADDRESS = USDC_ADDRESS if COLLATERAL_ASSET == "USDC" else BUIDL_ADDRESS
ORDER_SIDE = "REDEEM"  # MINT
MIN_MINT_AMOUNT = 25
MAX_MINT_AMOUNT = 9_900_000
ALLOW_INFINITE_APPROVALS = False

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
    return balance


def main():
    """
    Order flow
    """
    logging.info("Starting USDTB minting script...")
    if not all([PRIVATE_KEY, RPC_URL]):
        logging.error("Missing environment variables. Please check your .env file.")
        return
    if COLLATERAL_ASSET not in ["USDC", "BUIDL"]:
        logging.error("Invalid COLLATERAL_ASSET.")
        return
    if ORDER_SIDE not in ["MINT", "REDEEM"]:
        logging.error("Invalid side.")
        return
    mint_abi = load_abi("py/usdtb_mint_abi.json")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    # pylint: disable=no-value-for-parameter
    acc: LocalAccount = Account.from_key(PRIVATE_KEY)
    usdtb_minting_contract = w3.eth.contract(
        address=Web3.to_checksum_address(USDTB_MINTING_ADDRESS), abi=mint_abi
    )

    while True:
        try:
            collateral_balance = int(get_balance(w3, COLLATERAL_ASSET_ADDRESS)/10**6) - 1 #for minting
            usdtb_balance = int(get_balance(w3, USDTB_ADDRESS)/10**6) - 1 #for redeeming
            balance = collateral_balance if ORDER_SIDE == "MINT" else usdtb_balance
            print(f"BALANCE to {ORDER_SIDE}", balance)
            if balance < MIN_MINT_AMOUNT:
                time.sleep(10)
                continue
            rfq_amount = int(min(MAX_MINT_AMOUNT, balance))
            rfq_url = f"{USDTB_PUBLIC_URL}rfq?pair={COLLATERAL_ASSET}/USDtb&type_=ALGO&side={ORDER_SIDE}&size={rfq_amount}&benefactor={MULTISIG}"
            rfq_data = get_rfq_data(rfq_url)
            logging.info(rfq_url)
            logging.info(rfq_data)
            if rfq_data is None:
                return
            if ORDER_SIDE == "MINT":
                order = create_mint_order(rfq_data, MULTISIG, COLLATERAL_ASSET_ADDRESS)
            else:
                order = create_redeem_order(rfq_data, MULTISIG, COLLATERAL_ASSET_ADDRESS)
            signature = sign_order(w3, order, acc, usdtb_minting_contract)

            signature_hex = to_hex(signature.signature_bytes)
            order_url = f"{USDTB_PUBLIC_URL}order?signature={signature_hex}"

            try:
                logging.info(f"Submitting {ORDER_SIDE} order: {order}")
                response = requests.post(order_url, json=order, timeout=60)
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
        except Exception as e:
            # Can occur during api restarts
            logging.error(f"Global exception: {e}")
            time.sleep(13)

if __name__ == "__main__":
    main()
