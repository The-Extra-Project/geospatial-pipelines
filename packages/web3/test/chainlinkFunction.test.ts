import {requestFunctionContribution} from "chainlink-functions/request"
import {IndividualContributionStruct} from "../scripts/typechain-types/contracts/CircumToken"
describe("chainlink function call", async () => {
    
    it("it able to run function call" , async() => {
        let gasLimit: number = 300000
        let params: IndividualContributionStruct = {
            clientContribution: 90,
            reallignmentParameter:10
        }
       // await requestFunctionContribution(params,gasLimit)
    })




})