import ethers from "ethers"
import {CircumToken, CircumTokenInterface, IndividualContributionStruct } from "../typechain-types/contracts/CircumToken"
import { CircumToken__factory } from "../typechain-types"

/**
 * calls `CircumToken.addIndividualContributor(....) parameter `
 * @param walletInstance 
 */
const ContributeMetric = async (tokenAddress: string, signerInstance:  ethers.Signer, clientAddress: any, params: IndividualContributionStruct, contractFactory: CircumToken__factory ) => {
    const tokenInterface = new ethers.utils.Interface(CircumToken__factory.abi)
    const circumToken =  new ethers.Contract(tokenAddress,tokenInterface,signerInstance) as unknown as CircumToken
    await circumToken.addIndividualContribution(clientAddress, params)

    circumToken.on("IndividualContributionAdded", (address, params) => {
        console.log("the function is executed with the address: " + address + "and the parameters" + params)
    })
}