import {
  useAccount,
  useWaitForTransactionReceipt,
  useWriteContract,
} from "wagmi";

import { Address, erc20Abi, parseUnits } from "viem";
import { useSimulateContract } from "wagmi";
import { MINTING_ADDRESS, PAIR_TOKENS } from "@/app/constants/appConfig";
import { toast } from "react-toastify";
import { useEffect } from "react";

export const useApprove = ({
  amount,
  selectedTokenAddress,
}: {
  amount: number;
  selectedTokenAddress: Address;
}) => {
  const parsedAmount = BigInt(
    parseUnits(
      `${amount}`,
      PAIR_TOKENS.find((token) => token.address === selectedTokenAddress)
        ?.decimals ?? 6
    )
  );

  const { address } = useAccount();
  const {
    data: txHash,
    writeContract,
    isSuccess: isWriteSuccess,
  } = useWriteContract();

  const { data: simulateData } = useSimulateContract({
    account: address,
    abi: erc20Abi,
    address: selectedTokenAddress,
    functionName: "approve",
    args: [MINTING_ADDRESS, parsedAmount],
  });

  const onApprove = async () => {
    if (simulateData) {
      await writeContract(simulateData?.request);
    }
  };

  const { isSuccess, isError, isPending } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  useEffect(() => {
    if (isSuccess && txHash) {
      toast.success(`Approved: ${txHash}`);
    }
    if (isError) {
      toast.error("Error approving");
    }
  }, [isSuccess, isError, txHash]);

  return {
    isLoading: isPending && isWriteSuccess,
    onApprove,
  };
};
