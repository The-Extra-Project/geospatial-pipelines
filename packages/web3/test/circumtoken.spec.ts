import {tokenContractAPI} from "../scripts/tokenAPI"
import {deployContracts} from '../scripts/deploy'
import ethers from "ethers"
import {config} from "dotenv" 

let env_path: any = config({path: '../.env'})

describe("circumToken deployment", async () => {
    it("initializes the parameters of the token contract script", async () => {
        const wallet = new ethers.Wallet(env_path["PRIVATE_KEY"])
        const [tokenAddress, stakingAddress] = await deployContracts()
        const mumbai_testnet = "80001"
        const private_key = env_path["PRIVATE_KEY"]    
        let api = new tokenContractAPI(tokenAddress ,wallet.getAddress(), mumbai_testnet, private_key )
        console.log("address is deployed at" + api.circumTokenAddress);
        
        
        }
    ); 
})


