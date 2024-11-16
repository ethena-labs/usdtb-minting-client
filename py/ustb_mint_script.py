import json
import os
import time
from dataclasses import dataclass
from enum import IntEnum

import requests
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import to_hex, to_bytes
from web3 import Web3

env_path = find_dotenv()
load_dotenv(env_path)
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WEB3_URL = os.getenv("RPC_URL")
USTB_TOKEN_ADDRESS = Web3.to_checksum_address(os.getenv("USTB_TOKEN_ADDRESS", ""))
USTB_MINTING_ADDRESS = Web3.to_checksum_address(
    os.getenv("USTB_MINTING_CONTRACT_ADDRESS", "")
)


class SignatureType(IntEnum):
    EIP712 = 0
    EIP1271 = 1


@dataclass(init=True, order=True)
class Signature:
    signature_type: SignatureType
    signature_bytes: bytes


# production
ustb_public_url = " https://public.api.ustb.money/"
ustb_private_url = " https://private.api.ustb.money/"

# staging
ustb_public_url_staging = " https://public.api.staging.ustb.money/"
ustb_private_url_staging = " https://private.api.staging.ustb.money/"

if __name__ == "__main__":
    with open("ustb_mint_abi.json", encoding="utf-8") as f:
        mint_abi = json.load(f)

    with open("ustb_token_abi.json", encoding="utf-8") as f:
        ustb_abi = json.load(f)

    w3 = Web3(Web3.HTTPProvider(WEB3_URL))

    ustb_minting_contract = w3.eth.contract(address=USTB_MINTING_ADDRESS, abi=mint_abi)
    ustb_contract = w3.eth.contract(address=USTB_TOKEN_ADDRESS, abi=ustb_abi)

    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    buidl_address = "0x7712c34205737192402172409a8F7ccef8aA2AEc"

    type_ = "ALGO"
    side = "MINT"
    rfq_url = f"{ustb_public_url_staging}rfq?pair=USDC/UStb&type_={type_}&side={side}&size=25"
    response = requests.get(rfq_url, timeout=5)
    rfq_data = response.json()

    # your own private key. If you trade through smart contract and use delegateSigner, the private key of your delegated signer
    # pylint: disable=no-value-for-parameter
    acc: LocalAccount = Account.from_key(PRIVATE_KEY)
    print("rfq_data", rfq_data)
    print(acc.address)

    # order object sent back to /order endpoint
    mint_order = {
        "order_id": str(rfq_data["rfq_id"]),
        "order_type": side,
        "expiry": int(time.time() + 60),
        "nonce": int(time.time() + 60),
        "benefactor": acc.address,
        "beneficiary": acc.address,
        "collateral_asset": usdc_address,
        "collateral_amount": int(rfq_data["collateral_amount"]),
        "ustb_amount": int(rfq_data["ustb_amount"]),
    }

    # EIP712 signature struct
    # "Order(
    # string order_id,
    # uint8 order_type,
    # uint256 expiry,
    # uint256 nonce,
    # address benefactor,
    # address beneficiary,
    # address collateral_asset,
    # uint256 collateral_amount,
    # uint256 ustb_amount)"

    # Tuple for signing
    order_tuple = (
        str(mint_order["order_id"]),  # string order_id, use RFQ ID from /rfq payload
        (
            0 if mint_order["order_type"].upper() == "MINT" else 1
        ),  # uint8 order_type, 0 for mint, 1 for redeem
        mint_order["expiry"],  # uint256 expiry, use current time + 60s
        mint_order[
            "nonce"
        ],  # uint256 nonce, use unique int for each order (eg timestamp)
        w3.to_checksum_address(mint_order["benefactor"]),
        # address benefactor, address where token is taken out of. stETH for mint, UStb for redeem
        w3.to_checksum_address(mint_order["beneficiary"]),
        # address beneficiary, address where incoming token is received. UStb for mint, stETH for redeem
        w3.to_checksum_address(
            mint_order["collateral_asset"]
        ),  # address collateral_asset, stETH address
        mint_order[
            "collateral_amount"
        ],  # uint256 collateral_amount, use exact value provided in RFQ
        mint_order[
            "ustb_amount"
        ],  # uint256 ustb_amount, use exact value provided in RFQ
    )

    order_hash = ustb_minting_contract.functions.hashOrder(order_tuple).call()
    order_signed = acc.signHash(order_hash)
    order_rsv = (
        to_bytes(order_signed.r) + to_bytes(order_signed.s) + to_bytes(order_signed.v)
    )
    print("tuple", order_tuple)
    print("rsv", order_rsv)
    signature = Signature(SignatureType.EIP712, order_rsv)

    signature_hex = to_hex(signature.signature_bytes)
    print("hex", signature_hex)

    url = f"""{ustb_public_url_staging}order?signature={signature_hex}"""
    response = requests.post(url, json=mint_order, timeout=60)
    if "error" in response.json():
        print(response.json()["error"])
    else:
        tx_id = response.json()["tx"]
        print(f"https://etherscan.io/tx/{tx_id}")
