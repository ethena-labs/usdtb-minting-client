"use client";

import { LoadingWhitelist } from "@/app/components/features/mint/LoadingWhitelist";
import { Mint } from "@/app/components/features/mint/Mint";
import { NotConnected } from "@/app/components/features/mint/NotConnected";
import { NotWhitelisted } from "@/app/components/features/mint/NotWhitelisted";
import { useIsMounted } from "@/app/hooks/useIsMounted";
import { useWhitelistCheck } from "@/app/hooks/useWhitelistCheck";
import { useAccount } from "wagmi";

export default function Home() {
  const { address } = useAccount();
  const { isLoading: isCheckingWhitelist, isWhitelisted } = useWhitelistCheck();
  const isMounted = useIsMounted(0);

  if (!isMounted) return;

  if (!address) return <NotConnected />;

  if (isCheckingWhitelist) return <LoadingWhitelist />;

  if (!isWhitelisted)
    return <NotWhitelisted isWhitelisted={isWhitelisted ?? false} />;

  return <Mint />;
}
