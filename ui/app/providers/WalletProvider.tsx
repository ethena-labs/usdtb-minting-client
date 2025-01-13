"use client";
import "@rainbow-me/rainbowkit/styles.css";

import { getDefaultConfig, RainbowKitProvider } from "@rainbow-me/rainbowkit";
import { http, WagmiProvider } from "wagmi";
import { mainnet } from "wagmi/chains";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { MINTING_TOKEN_NAME } from "@/app/constants/appConfig";
import { createPublicClient } from "viem";

const projectId = process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID ?? "";

const queryClient = new QueryClient();

export const config = getDefaultConfig({
  appName: MINTING_TOKEN_NAME,
  projectId: projectId,
  chains: [mainnet],
  ssr: true,
});

export const publicClient = createPublicClient({
  chain: config.chains[0],
  transport: http(),
});

export const WalletProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>{children}</RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
};
