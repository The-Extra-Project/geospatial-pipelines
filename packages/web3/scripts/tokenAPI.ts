import { ethers } from 'hardhat';
import {
  CircumToken,
  IndividualContributionStruct,
} from '../typechain-types/contracts/CircumToken';
//const contractFactoryCircum = ethers.getContractFactory("CircumToken")

/**
 * a test script to test the functions on top of
 */

export class tokenContractAPI {
  CircumToken: any;
  circumTokenAddress: any;
  userWallet: any;
  provider: any;

  constructor(
    tokenContractAddress: string,
    _userAddress: any,
    network_key: any,
    private_key?: any
  ) {
    this.circumTokenAddress = tokenContractAddress;
    this.provider = new ethers.providers.AlchemyProvider(
      network_key,
      process.env.API_KEY
    );
    this.userWallet = new ethers.Wallet(
      private_key,
      new ethers.providers.AlchemyProvider(network_key, process.env.API_KEY)
    );
    this.CircumToken = ethers.getContractAt(
      'CircumToken',
      this.circumTokenAddress
    );
  }
  /**
   * @abstract function to setup the parameters (by the oracle bot).
   *
   * @returns
   *
   */
  async createParameters(
    address: typeof ethers.constants.AddressZero,
    inputParams: IndividualContributionStruct
  ): Promise<any> {
    let status_output;
    try {
      status_output = (await this.CircumToken)
        .addIndividualContribution(address, inputParams)
        .then((output: any) => {
          console.log('parameters added are:', output);
        });
    } catch (e: any) {
      console.error('err:  ' + e);
    }
    return status_output;
  }

  async mintingToken(
    address_to: typeof ethers.constants.AddressZero,
    amount: any
  ): Promise<any> {
    try {
      let function_call = (await this.CircumToken).mintToken(
        address_to,
        amount
      );

      console.log('token minted: ' + function_call);
      console.log(
        'balance of the account:',
        this.provider.getBalance(address_to)
      );
    } catch (e: any) {
      console.error('err in minting token result:  ' + e);
    }
  }
}
