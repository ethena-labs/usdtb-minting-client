# UStb TypeScript SDK

This SDK provides utilities for minting and redeeming UStb tokens.

## Setup

1. Install dependencies:

```bash
pnpm i
```

2. Set the environment variables:

```bash
cp .env.example .env
```

4. Set configuration in `mint_script.ts` - Specify the amount, collateral asset, benefactor, and side.

5. Approve tokens to be spent by the minting contract.  The spender is the minting contract address: `0x4a6B08f7d49a507778Af6FB7eebaE4ce108C981E`.

6. Run the script:

```bash
pnpm mint
```

## Instructions for use in a larger project

1. Copy all files except `mint_script.ts` to your project.
2. Add viem to your project dependencies.
3. Set the environment variables in your project.
4. Use the utility functions in mint_utils.ts to fetch quotes and generate, sign, and submit orders.
