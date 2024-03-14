import { Request, Response } from "express";
import { requestFunctionContribution } from "@web3/chainlink-functions/request"

export const run_compute_params = async (request: Request, response: Response, gasLimit: any = "30000"):Promise<void> => {
    try {
        let input_param : string[] = [request.query.collaboration_parameter as string, request.query.reallignment_parameter as string]
        await requestFunctionContribution(input_param, gasLimit)
    }
    catch (error) {
        console.error(error)
    }
}