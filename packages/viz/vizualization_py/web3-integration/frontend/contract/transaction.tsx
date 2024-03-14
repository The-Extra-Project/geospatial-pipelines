"use client";
import {TransactionReceipt} from "@ethersproject/providers";
import React, { useEffect, useState } from "react";
import { RelayTransactionResponse } from "@cometh/connect-sdk";
import { ethers } from "ethers";
import {AbstractedWalletCometh, IndividualContributionStruct} from "@dev-extralabs/web3/scripts/abstraction"
import {SupportedNetworks, ComethProvider, ComethWallet} from "@cometh/connect-sdk"
import { createContext } from "vm";
import walletAuthentication from "@/app/page"
export const TokenContractAddress = "0x66fd19Dcd8a8A144415b5C2274B6dD737f639B7B"

interface TransactionProps {
    transactionSuccess: boolean;
    setTransactionSuccess: React.Dispatch<React.SetStateAction<boolean>>;
}

type IndividualContribution =  {
actualContribution: ethers.BigNumberish,
recalibration: ethers.BigNumberish
}


let abstractWallet = new AbstractedWalletCometh(
     SupportedNetworks.MUMBAI as SupportedNetworks,
     "",
     TokenContractAddress,
     "malikdhruv1994@gmail.com"
)


// function walletAuthentication() {
//     const {
//       setWallet,
//       setProvider,
//       wallet,
//       tokenContract,
//       setTokenContract,
//     } = useWalletContext();
//     const [isConnecting, setIsConnecting] = useState(false);
//     const [isConnected, setIsConnected] = useState(false);
  
//     const [connectionError, setConnectionError] = useState<string | null>(null);

//     const apiKey = process.env.NEXT_PUBLIC_COMETH_API_KEY;

//     function displayError(message: string) {
//       setConnectionError(message)
//     }

//     async function connect() {
//       if (!apiKey) throw new Error("no apiKey provided");
//       setIsConnecting(true);
//       try {
//         const walletAdaptor = new ConnectAdaptor({
//           chainId: SupportedNetworks.MUMBAI,
//           apiKey,
//         });
  
//         const instance = new ComethWallet({
//           authAdapter: walletAdaptor,
//           apiKey,
//         });
  
//         const localStorageAddress = window.localStorage.getItem("walletAddress");
  
//         if (localStorageAddress) {
//           await instance.connect(localStorageAddress);
//         } else {
//           await instance.connect();
//           const walletAddress = await instance.getAddress();
//           window.localStorage.setItem("walletAddress", walletAddress);
//         }
  
//         const instanceProvider = new ComethProvider(instance);
  
//         const contract = new ethers.Contract(
//           TokenContractAddress,
//           _abi,
//           instanceProvider.getSigner()
//         );
  
//         setTokenContract(contract);
  
//         setIsConnected(true);
//         setWallet(instance as any);
//         setProvider(instanceProvider as any);
//       } catch (e) {
//         displayError((e as Error).message);
//       } finally {
//         setIsConnecting(false);
//       }
//     }
  
//     async function disconnect() {
//       if (wallet) {
//         try {
//           await wallet!.logout();
//           setIsConnected(false);
//           setWallet(null);
//           setProvider(null);
//           setTokenContract(null);
//         } catch (e) {
//           displayError((e as Error).message);
//         }
  
//       }

//     }
//     return {
//       wallet,
//       tokenContract,
//       connect,
//       disconnect,
//       isConnected,
//       isConnecting,
//       connectionError,
//       setConnectionError,
//     };
  
//   }

export function runSetIndividualContribution({
    transactionSuccess,
    setTransactionSuccess,
}: TransactionProps) {
    const { wallet } = walletAuthentication();
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
    const automatedTransaction = async (destination_address: string, active_contribution: number, recalibration: number) => {
        isTransactionInitiated(null);
        setTransactionResponse(null);
        setTransactionError(null);
        setTransactionSuccess(false);
        transactionLoaded(true);
        try {
            if (!wallet) throw new Error("No wallet instance");
            let contributionParams : IndividualContribution = {
                actualContribution: ethers.utils.parseEther(active_contribution.toString()),
                recalibration: ethers.utils.parseEther(recalibration.toString())
            }
            const txn: RelayTransactionResponse = await abstractWallet.addIndividualContribution(destination_address,contributionParams as unknown as IndividualContributionStruct)
            isTransactionInitiated(txn);
        }
        catch (e: any) {
            setTransactionError(e);
            transactionLoaded(false);
            setTransactionSuccess(false);
        }

    }


}


export function displayIndividualContributionButton({
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
