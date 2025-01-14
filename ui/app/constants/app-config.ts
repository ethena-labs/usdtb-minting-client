import { MINTING_CONTRACT_ABI } from "@/app/constants/minting-abi";

export const IS_PROD_ENV = process.env.NEXT_PUBLIC_APP_ENV !== "development";

export const MINTING_ABI = MINTING_CONTRACT_ABI;
export const MINTING_ADDRESS = "0xa3DDBf92077b850E29C4805Df0a2459Ae048416a";
export const MINTING_TOKEN_NAME = "USDtb";
export const MINTING_TOKEN_URL = process.env.NEXT_PUBLIC_MMAPI_URL ?? "";

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
export const GITHUB_URL = "https://github.com/ethena-labs";
export const GITBOOK_URL = "https://docs.usdtb.money/";
