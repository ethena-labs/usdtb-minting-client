"use client";

import { Box } from "@/app/components/Box";
import { Button } from "@/app/components/Button";
import { Input } from "@/app/components/Input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/Select";
import { MINTING_TOKEN_NAME, PAIR_TOKENS } from "@/app/constants/app-config";
import { useAllowance } from "@/app/hooks/useAllowance";
import { useApprove } from "@/app/hooks/useApprove";
import { useMint } from "@/app/hooks/useMint";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { Address } from "viem";
import { useState } from "react";

export const Mint = () => {
  const defaultTokenAddress = PAIR_TOKENS[0].address as Address;
  const [selectedTokenAddress, setSelectedTokenAddress] =
    useState(defaultTokenAddress);
  const [amount, setAmount] = useState<number | "">("");

  const { isAllowed, isCheckingAllowance } = useAllowance({
    amount: Number(amount),
    selectedTokenAddress,
  });

  const { onApprove, isLoading: isApproving } = useApprove({
    amount: Number(amount),
    selectedTokenAddress,
  });

  const { onMint, isLoading: isMinting } = useMint({
    amount: Number(amount),
    selectedTokenAddress,
  });

  const getButtonText = () => {
    if (isCheckingAllowance) {
      return "Checking allowance...";
    }

    if (isApproving) {
      return "Approving...";
    }

    if (isMinting) {
      return "Minting...";
    }

    if (isAllowed) {
      return "Mint";
    }

    return "Approve";
  };

  const isLoading = isCheckingAllowance || isApproving || isMinting;

  return (
    <Box>
      <div className="flex flex-col gap-8">
        <div className="flex flex-wrap justify-between items-center gap-2 sm:gap-10 w-full">
          <h1 className="text-2xl font-medium">Mint {MINTING_TOKEN_NAME}</h1>
          <ConnectButton showBalance={false} />
        </div>
        <div className="flex items-center justify-center gap-2">
          <Input
            placeholder="0"
            type="number"
            data-type="currency"
            value={amount}
            onChange={(e) =>
              e.target.value === ""
                ? setAmount("")
                : setAmount(Number(e.target.value))
            }
            disabled={isLoading}
          />
          <Select
            defaultValue={defaultTokenAddress}
            value={selectedTokenAddress}
            onValueChange={(value) => setSelectedTokenAddress(value as Address)}
            disabled={isLoading}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PAIR_TOKENS.map((token) => (
                <SelectItem key={token.name} value={token.address}>
                  {token.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          className="w-full"
          disabled={isLoading || !amount}
          onClick={isAllowed ? onMint : onApprove}
        >
          {isLoading && (
            <div className="bg-white mr-0.5 h-2 w-2 animate-pulse rounded-full" />
          )}
          {getButtonText()}
        </Button>
      </div>
    </Box>
  );
};
