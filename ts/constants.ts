import "dotenv/config";

export const ORDER_TYPE = {
  Order: [
    { name: "order_id", type: "string" },
    { name: "order_type", type: "uint8" },
    { name: "expiry", type: "uint120" },
    { name: "nonce", type: "uint128" },
    { name: "benefactor", type: "address" },
    { name: "beneficiary", type: "address" },
    { name: "collateral_asset", type: "address" },
    { name: "collateral_amount", type: "uint128" },
    { name: "ustb_amount", type: "uint128" },
  ],
} as const;
export const MINT_ADDRESS = "0x4a6B08f7d49a507778Af6FB7eebaE4ce108C981E";

export const DOMAIN = {
  chainId: 1,
  name: "UStbMinting",
  verifyingContract: MINT_ADDRESS,
  version: "1",
} as const;

export const USTB_URL = "https://public.api.staging.ustb.money/";

export const RPC_URL = process.env.RPC_URL as string;
