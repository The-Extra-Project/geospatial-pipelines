import {render} from "@testing-library/react"
import React from "react"
import {demoInjectWallet} from "./mock/frontend"

describe("wallet_modal", async () => {

   it("connects to the wallet parameter and gets address", async () => {
    const walletAddressRendering = render(<demoInjectWallet />)
    expect(walletAddressRendering).to.notBe(null)

   })
   

})
