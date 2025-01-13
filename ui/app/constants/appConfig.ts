import { MINTING_CONTRACT_ABI } from "@/app/constants/minting-abi";

export const IS_PROD_ENV = process.env.NEXT_PUBLIC_APP_ENV !== "development";

export const MINTING_ABI = MINTING_CONTRACT_ABI;
export const MINTING_ADDRESS = "0xdD7Ca5B25B2A857012537aA0393B4667B9824a72";
export const MINTING_TOKEN_NAME = "USDtb";
export const MINTING_TOKEN_URL = "https://public.api.staging.usdtb.money/";

export const PAIR_TOKENS = [
  {
    name: "USDC",
    address: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    decimals: 6,
  },
];

export const DOMAIN = {
  chainId: 1,
  name: "USDtbMinting",
  verifyingContract: MINTING_ADDRESS,
  version: "1",
} as const;

export const TOKEN_AMOUNT_FIELD = "usdtb_amount";
