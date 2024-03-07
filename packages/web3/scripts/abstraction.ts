// @ts-ignore
import {
  ComethProvider,
  ComethWallet,
  ConnectAdaptor,
  SupportedNetworks,
} from '@cometh/connect-sdk';
import { BigNumberish, ethers } from 'ethers';

import * as dotenv from 'dotenv';
dotenv.config();
import { CircumToken } from './typechain-types/';
import { CircumToken__factory } from '@dev-extralabs/web3/scripts/typechain-types';

/**
 * adding the window property inn order to avoid the error "Window not provided"
 * 
 */



/**
 * @abstract abstractedWallet implements the wrapper methods on top of cometh for users to login and create account on circum platform
 * using either of the verification techniques (biometrics or email based traditional OAuth using passport API).
 */

// @ts-ignore: no exported member 'wx'
export type IndividualContributionStruct = {
  clientContribution: BigNumberish;
  reallignmentParameter: BigNumberish;
};

export class AbstractedWalletCometh {
  chainId: any;
  private sessionToken: Map<string, string[]>; // this is the authentification token that is associated for given time once the Oauth is verified.
  private walletAdaptor: ConnectAdaptor;
  public wallet: ComethWallet;
  tokenContract: ethers.Contract;
  private provider: ComethProvider;
  constructor(
    chainId: SupportedNetworks,
    _validatedToken: any,
    tokenAddress: string,
    emailAddress: string
  ) {
    this.chainId = chainId;
    this.sessionToken = _validatedToken;
    this.walletAdaptor = new ConnectAdaptor({
      chainId: chainId,
      apiKey: process.env.COMETH_API_KEY || '',
    });

    this.wallet = new ComethWallet({
      authAdapter: this.walletAdaptor,
      apiKey: process.env.COMETH_API_KEY || '',
    });

    this.provider = new ComethProvider(this.wallet);

    // this.tokenContract = new tokenContractAPI(token, "80001", userId)
    const signer = this.provider.getSigner();
    this.tokenContract = new CircumToken__factory(signer).attach(tokenAddress);
    this.sessionToken.set(this.wallet.getAddress(), [emailAddress, _validatedToken]);
  }

  async connect(address: string): Promise<string> {

    const localStorageAddress = window.localStorage.getItem("walletAddress");

    if (localStorageAddress) {
      await this.wallet.connect(localStorageAddress);
    } else {
      await this.wallet.connect();
      const walletAddress = await this.wallet.getAddress();
      window.localStorage.setItem("walletAddress", walletAddress);
    }
    return await this.wallet.getAddress();
  }

  /**
   * mints the token (called by the address having minting role on the circumToken contract) to the data provider address.
   * @param destinationAddress data provider address
   */
  async mintTokenAddress(destinationAddress: string): Promise<void> {
    try {
      const txnMint = await this.tokenContract.mintToken(destinationAddress);
      const txnReceipt = await txnMint.wait();
      console.log(
        'and the transaction is executed w/ following txn receipt',
        txnReceipt
      );
    } catch (e: any) {
      console.log('exception caused in the mint token address function', e);
    }
  }

  /**
   * function called by the oracle contract in order to add the contribution parameter
   * @param destinationAddress is the address of the data provider that has to be attributed for their data format
   * @param contributionMetrics is the parameter corresponding to which your amount of the tokens are calculated.
   */
  async addIndividualContribution(
    destinationAddress: string,
    contributionMetrics: IndividualContributionStruct
  ) {
    try {
      const txnMint = await this.tokenContract.addIndividualContribution(
        destinationAddress,
        contributionMetrics
      );
      const txnReceipt = await txnMint.wait();
      console.log(
        'and the transaction is executed w/ following txn receipt',
        txnReceipt
      );
    } catch (e: any) {
      console.log(
        'exception caused in the individual contribution function',
        e
      );
    }
  }
  /**
   * 
   * @param currentAddress is the address of the data provider that has received token
   * @returns the balance of the given user.
   */
  async getMintedToken(currentAddress: string): Promise<BigNumberish> {
    let balance: BigNumberish = ethers.BigNumber.from(0);
    try {

      balance = await this.tokenContract.balanceOf(
        currentAddress
      );
    } catch (e: any) {
      console.log('exception caused in the getMintedToken function', e);
    }

    return balance;
  }

  /**Gets the parameter of each data provider's set address by the user.
   * @param userAddress: its the address of the suer whose dataset is defined and would like to get the contribution parameters.
   * @returns a struct consisting of the 2 parameters (those sum out to be 100) as the perfectages for the correct subtracted by the effort porvided by the offers.
   * 
   */
  async getIndividualContribution(userAddress: any): Promise<any> {
    let contributionParameters: any
    try {
      contributionParameters = await this.tokenContract.getIndividualContributions(userAddress)

    }
    catch (e: any) {
      console.error("exception caused in the getIndividualContributions")
    }

    return contributionParameters;
  }
}