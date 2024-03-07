import { AbstractedWalletCometh} from "../../scripts/abstraction"
import React from "react"
import { SupportedNetworks } from "@cometh/connect-sdk"

export let  demoInjectWallet = async (): Promise<React.ReactNode> => {
    let _validationToken = new Map()
    _validationToken.set("abc@def.com", ["<PASSWORD>"])
    const wallet = new AbstractedWalletCometh( SupportedNetworks.MUMBAI, _validationToken, "",  "abc@def.com" )
    return (
        <>
        <div>
        <h1>{wallet.wallet.getAddress()} </h1> 
         </div>
         </>
    )
}


