"use client";
import {TransactionReceipt} from "@ethersproject/providers";
import React, { useEffect, useState } from "react";
import {walletAuthentication} from "../pages/App"
import { RelayTransactionResponse } from "@cometh/connect-sdk";
import { ethers } from "ethers";

interface TransactionProps {
    transactionSuccess: boolean;
    setTransactionSuccess: React.Dispatch<React.SetStateAction<boolean>>;
}

type IndividualContribution =  {
actualContribution: ethers.BigNumberish,
recalibration: ethers.BigNumberish
}


export function runSetIndividualContribution({
    transactionSuccess,
    setTransactionSuccess,
}: TransactionProps) {
    const { wallet, tokenContract } = walletAuthentication();
    const [isTransactionLoading, transactionLoaded] = useState<boolean>(false);
    const [transactionError, setTransactionError] = useState(null);
    const [transactionInitiated, isTransactionInitiated] = useState<RelayTransactionResponse| null>(null);
    const [transactionResponse, setTransactionResponse] = useState<TransactionReceipt | null>(null);
    const [accountBalance, setAccountBalance] = useState<ethers.BigNumberish>();
    const [notIndiContribution, IndiContributionSet] = useState<boolean>(false);
    /**
     * fetches the individual contribution corresponding to each of the IPFS file that is submitted by the developer
     * 
     */
    function displayIndividualContributionButton({
        automatedTransaction,
        isTransactionLoading,

    }
    :
    {
        automatedTransaction: () => Promise<void>;
        isTransactionLoading:boolean
    })
    
    {
     
        return (
            <button className="mt-1 flex h-11 py-2 px-4 gap-2 flex-none items-center justify-center rounded-lg bg-gray-100 hover:bg-gray-200" onClick={automatedTransaction}>
            </button>

        )




        

    }
    const automatedTransaction = async () => {
        isTransactionInitiated(null);
        setTransactionResponse(null);
        setTransactionError(null);
        setTransactionSuccess(false);
        transactionLoaded(true);
        try {
            if (!wallet) throw new Error("No wallet instance");

            const tx: RelayTransactionResponse = await tokenContract.setIndividualContribution()
        }

    }












}