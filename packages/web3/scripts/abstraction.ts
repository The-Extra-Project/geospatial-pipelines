// @ts-ignore
import {ComethProvider, ComethWallet, ConnectAdaptor, SupportedNetworks} from "@cometh/connect-sdk"
import { BigNumberish, ethers} from "ethers"

import { config } from "dotenv"
import { CircumToken__factory } from "./typechain-types"



/**
 * @abstract abstractedWallet implements the wrapper methods on top of cometh for users to login and create account on circum platform
 * using either of the verification techniques (biometrics or email based traditional OAuth using passport API).
 */
config()



// @ts-ignore: no exported member 'wx'
export type IndividualContributionStruct = {
    clientContribution: BigNumberish;
    reallignmentParameter: BigNumberish;
  };

export class AbstractedWalletCometh {
    chainId: SupportedNetworks
    private sessionToken:  Map<string,string> // this is the authentification token that is associated for given time once the Oauth is verified.
    private walletAdaptor:  ConnectAdaptor
    public wallet: ComethWallet
    tokenContract: any 
    private provider: ComethProvider
    constructor(chainId: SupportedNetworks, _validatedToken: any, tokenAddress:string ) {
        this.chainId = chainId
        this.sessionToken = _validatedToken
        this.walletAdaptor = new ConnectAdaptor(
            {
                chainId:chainId,
                apiKey:process.env.COMETH_API_KEY || ''
                 
            }
        )
        
        this.wallet = new ComethWallet({
            authAdapter:this.walletAdaptor,
            apiKey: process.env.COMETH_API_KEY || '',
            rpcUrl: process.env.RPC || 'https://api.connect.cometh.io/',
        })

        this.provider = new ComethProvider(this.wallet)

       // this.tokenContract = new tokenContractAPI(token, "80001", userId)
       const signer = this.provider.getSigner()
        this.tokenContract = new ethers.Contract(tokenAddress,CircumToken__factory.abi,signer )
    
    }

    async connect(address: string): Promise<string> {
        await this.walletAdaptor.connect(address)
        return await this.wallet.getAddress()

    }
    
    /**
     * mints the token (called by the address having minting role on the circumToken contract) to the data provider address.
     * @param destinationAddress 
     * @param amount 
     */
    async mintTokenAddress(
        destinationAddress: string,
    ): Promise<void> {

        try {
        const txnMint = await this.tokenContract.mintToken(destinationAddress)
        const txnReceipt = await txnMint.wait()
        console.log("and the transaction is executed w/ following txn receipt", txnReceipt)
        }
        catch(e: any) {
            console.log("exception caused in the mint token address function", e)
        }
    }

    /**
     * function called by the oracle contract in order to add the contribution parameter
     */
    async addIndividualContribution(
        destinationAddress: string,
        contributionMetrics: IndividualContributionStruct
    ) {
        try {
            const txnMint = await this.tokenContract.addIndividualContribution(destinationAddress, contributionMetrics)
            const txnReceipt = await txnMint.wait()
            console.log("and the transaction is executed w/ following txn receipt", txnReceipt)
        }
        catch(e: any) {
            console.log("exception caused in the individual contribution function", e)
        }
    }
    async getMintedToken(currentAddress: string): Promise<BigNumberish>
    {   let balance: BigNumberish = ethers.BigNumber.from(0)
        try {
            const balance: BigNumberish = await this.tokenContract.balanceOf(currentAddress)
        }
        catch(e: any) {
            console.log("exception caused in the getMintedToken function", e)
        }

        return balance

    }





}

let test = true
//for testing 
if (test ) {
const tokenAddress = "0x66fd19Dcd8a8A144415b5C2274B6dD737f639B7B"
const oracleAddress = "0x36E8895442C8D90419a0a791D117339B78CbB656"
let  sessionToken : Map<string,string> = new Map()
sessionToken.set("0x36E8895442C8D90419a0a791D117339B78CbB656","testAuth")
let abstractToken = new AbstractedWalletCometh(SupportedNetworks.MUMBAI, sessionToken, tokenAddress)

const parameter_vars: IndividualContributionStruct = {
    clientContribution: "90",
    reallignmentParameter: "10"
  }
async() => {
    console.log("wallet getting connected w/ params", abstractToken.connect("0x36E8895442C8D90419a0a791D117339B78CbB656"))
await abstractToken.addIndividualContribution(oracleAddress, parameter_vars)
await abstractToken.mintTokenAddress(oracleAddress)

}
}
