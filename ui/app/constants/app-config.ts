import { MINTING_CONTRACT_ABI } from "@/app/constants/minting-abi";

export const IS_PROD = false; // set to true for production minting

export const MINTING_ABI = MINTING_CONTRACT_ABI;
export const MINTING_ADDRESS = IS_PROD
  ? "0xa3DDBf92077b850E29C4805Df0a2459Ae048416a"
  : "0xdD7Ca5B25B2A857012537aA0393B4667B9824a72";
export const MINTING_TOKEN_NAME = "USDtb";
export const MINTING_TOKEN_URL = IS_PROD
  ? "https://public.api.usdtb.money/"
  : "https://public.api.staging.usdtb.money/";

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
export const WAGMI_PROJECT_ID = "4b4cd8ea5a7805c848fd89f3a0132307";
