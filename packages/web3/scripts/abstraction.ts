
import {ComethWallet, ConnectAdaptor, SupportedNetworks} from "@cometh/connect-sdk"
import {ethers} from "ethers"
import {tokenContractAPI} from "./contractAPI"
/**
 * @abstract abstractedWallet implements the wrapper methods on top of cometh for users to login and create account on circum platform
 * using either of the verification techniques (biometrics or email based traditional OAuth using passport API).
 */

import { config } from "dotenv"

config(
    {
        path: "../../.env"
    }
)

class AbstractedWalletCometh {
    
    chainId: SupportedNetworks
    private sessionToken: Map<any,any> // this is the authentification token that is associated for given time once the Oauth is verified.
    private walletAdaptor:  ConnectAdaptor
    private wallet: ComethWallet
    constructor(chainId: SupportedNetworks, apiKey:string, _validatedToken: any, userId: string ) {
        this.chainId = chainId
        this.sessionToken = _validatedToken
        this.walletAdaptor = new ConnectAdaptor(
            {
                chainId:chainId,
                apiKey:apiKey
                 
            }
        )
        
        this.wallet = new ComethWallet({
            authAdapter:this.walletAdaptor,
            apiKey: process.env['API_KEY'] || '',
            rpcUrl: process.env['RPC'] || '',
        })
        tokenContract = 
    }
    
    createTokenMintingTransaction(

    )







    
}