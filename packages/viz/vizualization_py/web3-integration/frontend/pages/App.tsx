import React, {useContext,createContext, useState, Dispatch, SetStateAction} from "react";
import {
    ComethProvider,
    ComethWallet,
    ConnectAdaptor,
    SupportedNetworks,
  } from "@cometh/connect-sdk";
import { ethers } from "ethers";
import {_abi} from "../contract/tokenABI"
import {CheckCircledIcon} from "@radix-ui/react-icons"
import {UploadIcon} from "@radix-ui/react-icons"

import {CircumToken} from "@dev-extralabs/web3/dist/scripts/typechain-types/contracts"


export const WalletContext = createContext<{
    wallet: ComethWallet | null;
  setWallet: Dispatch<SetStateAction<ComethWallet | null>>;
  provider: ComethProvider | null;
  setProvider: Dispatch<SetStateAction<ComethProvider | null>>;
  tokenContract: ethers.Contract | null;
  setTokenContract: Dispatch<SetStateAction<ethers.Contract | null>>;
}>({
    wallet: null,
    setWallet: () => {},
    provider: null,
    setProvider: () => {},
    tokenContract: null,
    setTokenContract: () => {},
    })

        /**
* Hook to get wallet context values from WalletContext.
* Returns wallet, setWallet, provider, setProvider, 
* tokenContract, and setTokenContract.
*/
export function useWalletContext() {
  const {
    wallet,
    setWallet,
    provider,
    setProvider,
    tokenContract,
    setTokenContract,
  } = useContext(WalletContext);
  return {
    wallet,
    setWallet,
    provider,
    setProvider,
    tokenContract,
    setTokenContract,
  };
}
    

    export function walletProvider({children}:{children: React.ReactNode}): JSX.Element {

      const [wallet, setWallet] = useState<ComethWallet | null>(null);
      const [provider, setProvider] = useState<ComethProvider | null>(null);
      const [tokenContract, setTokenContract] = useState<ethers.Contract | null>(null);

      return(
        <WalletContext.Provider value ={{
          wallet,
          setWallet,
          provider,
          setProvider,
          tokenContract,
          setTokenContract
        }}
        >
          {children}

        </WalletContext.Provider>
      );

    }


    export function walletAuthentication() {

      const {
        setWallet,
        setProvider,
        wallet,
        tokenContract,
        setTokenContract,
      } = useWalletContext();
      const [isConnecting, setIsConnecting] = useState(false);
      const [isConnected, setIsConnected] = useState(false);
    
      const [connectionError, setConnectionError] = useState<string | null>(null);

      const apiKey = process.env.NEXT_PUBLIC_COMETH_API_KEY;
      const TokenContractAddress = "0x66fd19Dcd8a8A144415b5C2274B6dD737f639B7B"

      function displayError(message: string) {
        setConnectionError(message)
      }

      async function connect() {
        if (!apiKey) throw new Error("no apiKey provided");
        setIsConnecting(true);
        try {
          const walletAdaptor = new ConnectAdaptor({
            chainId: SupportedNetworks.MUMBAI,
            apiKey,
          });
    
          const instance = new ComethWallet({
            authAdapter: walletAdaptor,
            apiKey,
          });
    
          const localStorageAddress = window.localStorage.getItem("walletAddress");
    
          if (localStorageAddress) {
            await instance.connect(localStorageAddress);
          } else {
            await instance.connect();
            const walletAddress = await instance.getAddress();
            window.localStorage.setItem("walletAddress", walletAddress);
          }
    
          const instanceProvider = new ComethProvider(instance);
    
          const contract = new ethers.Contract(
            TokenContractAddress,
            _abi,
            instanceProvider.getSigner()
          );
    
          setTokenContract(contract);
    
          setIsConnected(true);
          setWallet(instance as any);
          setProvider(instanceProvider as any);
        } catch (e) {
          displayError((e as Error).message);
        } finally {
          setIsConnecting(false);
        }
      }
    
      async function disconnect() {
        if (wallet) {
          try {
            await wallet!.logout();
            setIsConnected(false);
            setWallet(null);
            setProvider(null);
            setTokenContract(null);
          } catch (e) {
            displayError((e as Error).message);
          }
    
        }

      }
      return {
        wallet,
        tokenContract,
        connect,
        disconnect,
        isConnected,
        isConnecting,
        connectionError,
        setConnectionError,
      };
    
    }

    interface ConnectUIWalletModalProps {
      connectionError: string | null;
  isConnecting: boolean;
  isConnected: boolean;
  connect: () => Promise<void>;
  wallet: ComethWallet;
    }


function walletUIModal({
  connectionError,
  isConnecting,
  isConnected,
  connect,
  wallet
}: ConnectUIWalletModalProps ): JSX.Element  {

  const fetchParamsButton =() => {

    if(isConnected) {
      return (
        <>
        <CheckCircledIcon width={30} height={20}/>
        <a
            href={`https://mumbai.polygonscan.com/address/${wallet.getAddress()}`}
            target="_blank"
          >
            {"Wallet connected"}        
        </a>
        </>

      )
    } else if (isConnecting) {
      return (
        <>
          <UploadIcon className="h-6 w-6 animate-spin" />
          {"Getting wallet..."}
        </>
      );
    }
    else {
      return "Get your Wallet";
    }



  }

  return (
    <>
      {!connectionError ? (
        <button
          disabled={isConnecting || isConnected || !!connectionError}
          className="flex items-center justify-center gap-x-2.5 p-3 font-semibold text-gray-900 hover:bg-gray-100 disabled:bg-white"
          onClick={connect}
        >
          {fetchParamsButton()}
        </button>
      ) : (
        <p className="flex items-center justify-center text-gray-900 bg-red-50">
          Connection didnt worked , check the cometh for queries or fetch logs
        </p>
      )}
    </>
  );
}
