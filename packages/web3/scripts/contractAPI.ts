import {ethers} from "hardhat"
import {CircumToken, IndividualContributionStruct } from '../typechain-types/contracts/CircumToken'
import {CircumToken__factory} from '../typechain-types/factories/contracts/CircumToken__factory'
import { MinEthersFactory } from "../typechain-types/common"
import { HardhatEthersHelpers } from "hardhat/types"
//const contractFactoryCircum = ethers.getContractFactory("CircumToken")



class tokenContractAPI {
    CircumToken: Promise<CircumToken>
    circumTokenAddress: typeof ethers.ZeroAddress
    userAddress: typeof ethers.ZeroAddress
    userWallet:  any
    provider: any
    constructor(tokenContractAddress: typeof ethers.ZeroAddress, _userAddress: any, network_key: any, private_key ?: any ) {
        this.circumTokenAddress = tokenContractAddress
        this.userAddress = _userAddress
        this.userWallet =  new ethers.Wallet(private_key,new ethers.AlchemyProvider(network_key,process.env.API_KEY))
        this.CircumToken = ethers.getContractAt("CircumToken",this.circumTokenAddress)
    }
    /**
     * @abstract function to setup the parameters (by the oracle bot).
     * 
     * @returns 
     * 
     */
    async createParameters( address: typeof ethers.ZeroAddress,inputParams:IndividualContributionStruct ): Promise<any> {
        let status_output;
        try {
        status_output = (await this.CircumToken).addIndividualContribution(address,inputParams).then((output) => {
        });

        }
        catch(e: any) {
            console.error('err:  ' + e)
        }
        return status_output;
        }


    async mintingToken(): Promise<any> {}

}