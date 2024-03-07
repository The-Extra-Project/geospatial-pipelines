import  ethers  from  "ethers"
import {CircumToken, CircumTokenInterface, IndividualContributionStruct } from "scripts/typechain-types/contracts/CircumToken"
import { CircumToken__factory } from "scripts/typechain-types"


const tokenInterface = new ethers.utils.Interface(CircumToken__factory.abi)

/**
 * calls `CircumToken.addIndividualContributor(....)`
 * @param walletInstance 
 */
const ContributeMetric = async (tokenAddress: string, signerInstance:  any, clientAddress: any, params: IndividualContributionStruct ) => {
    const circumToken =  new ethers.Contract(tokenAddress,tokenInterface,signerInstance) as unknown as CircumToken
    await circumToken.addIndividualContribution(clientAddress, params)
    console.log("the function call for contribution metric is executed")

    circumToken.on("IndividualContributionAdded", (address, params) => {
        console.log("the function is executed with the address: " + address + "and the parameters" + params)
    })
}


const MintingToken = async (tokenAddress: string,signerInstance:  ethers.Signer, clientAddress: any ) => {
    const circumToken =  new ethers.Contract(tokenAddress,tokenInterface,signerInstance) as unknown as CircumToken
    await circumToken.mintToken(clientAddress)
    // getting event TokenMinted

    circumToken.on("TokenMinted", async (address, params) => {
        const bal = await circumToken.balanceOf(address)
        console.log("the function is executed and current balanace of " + address + "is : " + bal)
    })
}