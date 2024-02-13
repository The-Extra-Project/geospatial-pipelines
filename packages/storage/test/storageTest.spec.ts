import assert from "assert"
import  lighthouse from '@lighthouse-web3/sdk'
import axios from "axios"
import {LighthouseStorageAPI} from '../Storage'
import { ethers } from "ethers"
import {expect, it, describe} from '@jest/globals';


// {
//   data: [
//     {
//       Name: 'decrypt.js',
//       Hash: 'QmeLFQxitPyEeF9XQEEpMot3gfUgsizmXbLha8F5DLH1ta',
//       Size: '1198'
//     }
//   ]
// }
const provider =  new ethers.providers.AlchemyProvider('Mumbai', `${process.env.API_KEY_ALCHEMY}`)

const user1 = new LighthouseStorageAPI('abc@gmail.com','0x81477cF7AB5Ed1eD309cc2640C4474EC38855046', provider,'0x')
const user2 = new LighthouseStorageAPI('def@gmail.com', '0xbADEeA5fA6462Aaeb5c37586312bC0d5C62074F3', provider, '0x')

let cid_stored_user1 = 'QmdrEBS1pEm1zgtMXwm1SFQKrsPCxSyifTA9dSCZ2Rhhcn'


describe(
    "lighthouse web API", async () => {
        it('is able to login and upload encrypted file',async () => {
        const result_json = user1.uploadDatasetEncrypted('./demo_pointcloud.xyz')[0]
        const ipfs_hash = result_json['Hash']
        const size = result_json['Size']
        expect(ipfs_hash).not.toBe(null)
        expect(size).not.toBe(null)


      })  

      it('is able to get the verifiable proof of the previously uploaded file',async () => {
        
        let fileAccess_user1  = user1.verificationProof(cid_stored_user1)
        expect(fileAccess_user1).toBe(true)  
      })


      it('is able to then revoke the access of the specific file and provide it to the other address user',async (

      ) => {

      const user2Wallet = new ethers.Wallet('')
      // here the privKey of the second user needs to be provided
      user1.transferOwnership(user2.pubKey,cid_stored_user1,user2Wallet.privateKey)
      let fileAccess_user1  = user1.verificationProof(cid_stored_user1)
      let fileAccess_user2 = user2.verificationProof(cid_stored_user1)
      expect(fileAccess_user1).toBe(false)
      expect(fileAccess_user2).toBe(true)        
      })

     


    }
)