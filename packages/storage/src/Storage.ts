/**
 * NOTE: Credits to the lighthouse and web3Storage documentation for developing the API's 
 * 
 */

import lighthouse from '@lighthouse-web3/sdk'
import {apiKeyResponse} from '@lighthouse-web3/sdk/dist/Lighthouse/getApiKey'
//import { getAccessCondition, generate, accessControl } from '@lighthouse-web3/kavach'
import {ethers} from 'ethers'
import kavach from "@lighthouse-web3/kavach"
import {sign} from "jsonwebtoken"
import fs from "fs"
import axios from "axios"
import dotenv from "dotenv"

/**
 * class that implements functionality with lighthouse to fetch, store or instantiate the deal for storage etc.
 * NOTE: there services are now payable and capped till certain range.
 * 
 */

dotenv.config(
    {
        path: '.env'
    }
)

export class LighthouseStorageAPI {
    userId: string
    lighthouseWallet: ethers.Wallet
    pubKey: string
    private provider?: any
    private apiKey: string
    baseURL: string // the backend uri for the user in order to get access to their gateway. user needs to setup their API key in order to get started.
    /**
     * @param userdetails are the current owner that wants to operate on the dataset (which is usually admin). 
     * NOTE: based on the various operations (client bidding successfully for the dataset ) will replace the current owner
     * @param password are the credential for opening the dataset.
     */
    constructor(userdetails, _pubKey, provider?: any, priv_key?: string) {
        this.userId = userdetails
        this.pubKey = _pubKey
        this.provider = provider
        this.lighthouseWallet = new ethers.Wallet(process.env.PRIV_KEY || priv_key || '')
        this.baseURL = 'https://api.lighthouse.storage/api/'
        this.apiKey = process.env.API_KEY 
    }


    /**
     * 
     * @param privKey the user wallet key (currently from the non custodial wallets, its not safe and DO NOT PUT THIS INTO PROD)
     * @param verificationMesg  is the associated crednetials (either the json verified message for transaction / login etc)
     */

    private async getAPIKey(privKey): Promise<apiKeyResponse> {
        const wallet = {publicKey: this.pubKey , privateKey: privKey || process.env.API_KEY }

        const verificationMesg = (await axios.get(this.baseURL + `auth/get_message?publicKey?=${wallet.publicKey}`)).data

        const signer = new ethers.Wallet(privKey)
        const signedMessage = await signer.signMessage(verificationMesg)
        
        return await lighthouse.getApiKey(wallet.publicKey, signedMessage)
    }
    /**
     * 
     * @param filepath the file that you want to upload in the lighthouse.
     * @returns the identifier (CID or fielcoin hash storage identifier) for the storage.
     */
    async uploadDatasetEncrypted(filepath:string) {

        const signedMessage = async () => {
            const provider = new ethers.providers.JsonRpcProvider(process.env.URI)
            const authMessage = await kavach.getAuthMessage(this.lighthouseWallet.address)
            const signedMessage = await this.lighthouseWallet.signMessage(authMessage.message as string)
            const { JWT, error } = await kavach.getJWT(this.lighthouseWallet.address, signedMessage)
            return (JWT)
        }
        try {
            if (filepath.split('.').pop() != ('.xyz' || '.laz') ) { 
                throw new Error("should be uplaoding the correct format of pointcloud file ")
            }
            let uploadObject = await lighthouse.uploadEncrypted(filepath, process.env.API as string, this.pubKey, (signedMessage as unknown) as string)        
            console.log("The file was saved successfully at + " + uploadObject["Hash"] + " along with ownership " + this.userId)
            return uploadObject["Hash"]
        } catch (error) {
            console.log(error)
        }
    }
    /**
     * 
     * @param newOwner defines the id of the new owner that will take the place of the given user in order to decrypt.
     * @param delegatedWallet is the address of the wallet that gets the address.
     * @param cid is the address that corresponds to the various wallets for getting 
     */
    async transferOwnership(newOwner: string, cid: string, delegatedWallet: any) {
        const generateAuthToken = async (delegatedWallet: string): Promise<string> => {
            return (sign(
                {
                    payload: this.lighthouseWallet
                    ,
                    delegatedWallet,
                }, process.env.PRIV_KEY, {
                expiresIn: "3600" // only one hr time for the file streaming (but can be adapted in case of large file storage and migration).
            }))

        }
        await kavach.revokeAccess(newOwner, cid, await generateAuthToken(delegatedWallet), delegatedWallet)
    }

    async authMessage(publicKey: string): Promise<string> {
        //const signer = new ethers.Wallet(process.env.PRIV_KEY || '', this.provider)
        const messageRequested = (await lighthouse.getAuthMessage(publicKey)).data.message
        const signedMessage = await this.lighthouseWallet.signMessage(messageRequested)
        return signedMessage
    }

    async decryptFile(
        cid_file: string, publicKey: string, filenamePATH: string
    ) {
        let authMessage = await this.authMessage(publicKey)
        let fileEncryptionKey = await lighthouse.fetchEncryptionKey(
            cid_file, publicKey, await this.authMessage(publicKey)
        )

        const decryptedData = await lighthouse.decryptFile(
            cid_file, fileEncryptionKey.data.key || ''
        )
        fs.createWriteStream(filenamePATH).write(Buffer.from(decryptedData))
    }

    /** 
     * function that gives the response whether a given file CID is stored on the filecoin network is authenticated verified or not.
     * @param cid is the file cid that you want to get the verification of.
     */
    async verificationProof(cid: string): Promise<boolean> {
        // first getting the proof of data segment inclusion
        let podsi
        let response
        try 
        {
        response = await axios.get(this.baseURL + `get_proof?cid=${cid}`)
        console.log(`getting the data segment proof : %s`, response.data )
        podsi = response.data
        }
        catch(error) {
            if (error instanceof Error) {
                console.error(error)
            }
        }
        const {pieceCID, dealInfo } = podsi
        
        if (!pieceCID || !dealInfo || dealInfo.length === 0 || !dealInfo.every(deal => deal.dealId && deal.storageProvider)) {
            console.error('Verification Failed');
            return false;
        }
        console.log('Document Verified:', pieceCID);
        return true;
    }


}




