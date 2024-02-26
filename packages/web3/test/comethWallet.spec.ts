import {AbstractedWalletCometh} from "../scripts/abstraction"
import { SupportedNetworks } from "@cometh/connect-sdk"
import ethers from "ethers"
import {config} from "dotenv" 
import {describe, expect, it} from "@jest/globals"

config()


describe("cometh wallet test", async () => {
    
    let abstractedWallet: AbstractedWalletCometh;
    abstractedWallet = new AbstractedWalletCometh(SupportedNetworks.MUMBAI, new Map(), "", "malikdhruv1994@gmail.com")        
    it("initializes the wallet on the cometh account", async () => {
        console.log("wallet initialized with parameters ")
        expect(abstractedWallet.chainId).toEqual(SupportedNetworks.MUMBAI)
        expect(abstractedWallet.tokenContract).toBeDefined()
    })

    it("mints the token for the client address by only the address designated as MINTER role", async () => {
        const minterAddress = ""
        const amount = "100"
        await abstractedWallet.mintTokenAddress(minterAddress);
        expect(abstractedWallet.getMintedToken(minterAddress)).toEqual(amount)
    })

})