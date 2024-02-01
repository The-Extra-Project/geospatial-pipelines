/**
 * credits to the chainlink-examples: https://github.com/smartcontractkit/smart-contract-examples/blob/main/functions-examples/examples/
 * 
 * Script for chainlink-functions for generating the 
 */

import fs from "fs"
import {
    SubscriptionManager,
    simulateScript,
    ResponseListener,
    ReturnType,
    decodeResult,
    FulfillmentCode,
} from "@chainlink/functions-toolkit"

import FunctionsClient from "@chainlink/contracts/abi/v0.8/FunctionsClient.json"

import path from "path"

//import {configContracts} from '../config'

import { ethers } from "ethers";

import { config } from "@chainlink/env-enc";


const consumerAddress = "" // its the address for the deployed circum token
const subscriptionId = ""; // also generated after the signing the transaction following the steps here: https://docs.chain.link/chainlink-functions/resources/architecture#subscription-management


const requestFunctionContribution = async (args: any, gasLimit: number) => {

    // parameters are defined on the 
    const routerAddress = "0x6E2dc0F9DB014aE19888F539E59285D2Ea04244C";
    const linkTokenAddress = "0x326C977E6efc84E512bB9C30f76E30c160eD06FB";
    const donId = "fun-polygon-mumbai-1";
    const explorerUrl = "https://mumbai.polygonscan.com";

    const fileSrc = fs.readFileSync(path.resolve(__dirname, './compute-score.ts')).toString()
    const rpcUrl = process.env.POLYGON_MUMBAI_RPC_URL; // fetch mumbai RPC URL
    const provider = new ethers.providers.JsonRpcProvider(rpcUrl);

    const wallet = new ethers.Wallet(process.env.PRIV_KEY as any)
    const signer = await (wallet.connect(provider) as ethers.Signer)

    console.log('running the compute-score function on chainlink functions onchain .....')

    try {
        const response = await simulateScript({
            source: fileSrc,
            args: args,
            bytesArgs: [], // bytesArgs - arguments can be encoded off-chain to bytes.
            secrets: {}, // no secrets in this example       
        })
        console.log("Simulation result", response);

        const returnType = ReturnType.uint256;
        const responseBytesHexstring = (response.responseBytesHexstring as unknown) as number;
        if (ethers.utils.arrayify(responseBytesHexstring).length > 0) {
            const decodedResponse = decodeResult(
                response.responseBytesHexstring || '',
                returnType
            );
            console.log(`✅ Decoded response to ${returnType}: `, decodedResponse);


        }

        console.log('now determining the subscription costs:')

        const subscriptionMngr = new SubscriptionManager({
            signer: signer, linkTokenAddress: linkTokenAddress, functionsRouterAddress: routerAddress
        });

        await subscriptionMngr.initialize();
        console.log("subscription manager initialized")
        const gasPriceWei = await signer.getGasPrice(); // get gasPrice in wei    

        try {
            const costInJuels = await subscriptionMngr.estimateFunctionsRequestCost({
                donId: donId,
                callbackGasLimit: gasLimit,
                subscriptionId: subscriptionId,
                gasPriceWei: gasPriceWei as unknown as bigint
            })

            console.log(`cost to complete the transaction ${ethers.utils.formatEther(costInJuels)} LINK`)

        }

        catch (e: any) { console.error('error during calculation of cost parameter:',) }
    
    console.log('running the final request by calling the consumer function abi')
    
    const functionsConsumerAbi = FunctionsClient

    const  functionsConsumer = new ethers.Contract(
        consumerAddress,
        functionsConsumerAbi,
        signer
      );


    const trnx = await functionsConsumer.sendRequest(fileSrc,"0x",0,0,args,[], subscriptionId, gasLimit, ethers.utils.formatBytes32String(donId));
    
    
    // Log transaction details
  console.log(
    `\n✅ Functions request sent! Transaction hash ${trnx.hash}. Waiting for a response...`
  );

  console.log(
    `See your request in the explorer ${explorerUrl}/tx/${trnx.hash}`
  );

  /**
   * The code below taken with full credits to https://github.com/smartcontractkit/smart-contract-examples/blob/main/functions-examples/examples/1-simple-computation/request.js#L138C1-L205C8
   */

  const responseListener = new ResponseListener({
    provider: provider,
    functionsRouterAddress: routerAddress,
  }); // Instantiate a ResponseListener object to wait for fulfillment.
  (async () => {
    try {
      const response: any = await new Promise((resolve, reject) => {
        responseListener
          .listenForResponseFromTransaction(trnx.hash)
          .then((response) => {
            resolve(response); // Resolves once the request has been fulfilled.
          })
          .catch((error) => {
            reject(error); // Indicate that an error occurred while waiting for fulfillment.
          });
      });

      const fulfillmentCode = response.fulfillmentCode;

      if (fulfillmentCode === FulfillmentCode.FULFILLED) {
        console.log(
          `\n✅ Request ${
            response.requestId
          } successfully fulfilled. Cost is ${ethers.utils.formatEther(
            response.totalCostInJuels
          )} LINK.Complete reponse: `,
          response
        );
      } else if (fulfillmentCode === FulfillmentCode.USER_CALLBACK_ERROR) {
        console.log(
          `\n⚠️ Request ${
            response.requestId
          } fulfilled. However, the consumer contract callback failed. Cost is ${ethers.utils.formatEther(
            response.totalCostInJuels
          )} LINK.Complete reponse: `,
          response
        );
      } else {
        console.log(
          `\n❌ Request ${
            response.requestId
          } not fulfilled. Code: ${fulfillmentCode}. Cost is ${ethers.utils.formatEther(
            response.totalCostInJuels
          )} LINK.Complete reponse: `,
          response
        );
      }

      const errorString = response.errorString;
      if (errorString) {
        console.log(`\n❌ Error during the execution: `, errorString);
      } else {
        const responseBytesHexstring = response.responseBytesHexstring;
        if (ethers.utils.arrayify(responseBytesHexstring).length > 0) {
          const decodedResponse = decodeResult(
            response.responseBytesHexstring,
            ReturnType.uint256
          );
          console.log(
            `\n✅ Decoded response to ${ReturnType.uint256}: `,
            decodedResponse
          );
        }
      }
    } catch (error) {
      console.error("Error listening for response:", error);
    }
  })();
    
    }

    catch (e: any) {
        console.error('in the outer function for execution of contribution function')
    }

}