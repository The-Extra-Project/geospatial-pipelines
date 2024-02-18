import * as process from "process";
import * as path from "path";
import * as fs from "fs";
import { startLocalFunctionsTestnet } from "@chainlink/functions-toolkit";
import { utils, Wallet } from "ethers";
import { config } from "@chainlink/env-enc";
import * as envConfig from "@chainlink/env-enc/dist/EncryptedEnv";

//import {dotenv} from "dotenv"
// Load environment variables from .env.enc file (if it exists)
const envConfig: encryptedEnc = require("../.env.enc");

envConfig.load();

(async () => {
  const requestConfigPath = path.join(process.cwd(), "functions-request-config.js"); // @dev Update this to point to your desired request config file
  console.log(`Using Functions request config file ${requestConfigPath}\n`);

  const localFunctionsTestnetInfo = await startLocalFunctionsTestnet(
    requestConfigPath,
    {
      logging: {
        debug: false,
        verbose: false,
        quiet: true, // Set this to `false` to see logs from the local testnet
      },
    }
  );

  console.table({
    "FunctionsRouter Contract Address": localFunctionsTestnetInfo.functionsRouterContract.address,
    "DON ID": localFunctionsTestnetInfo.donId,
    "Mock LINK Token Contract Address": localFunctionsTestnetInfo.linkTokenContract.address,
  });

  // Fund wallets with ETH and LINK
  const addressToFund: string = new Wallet(process.env["PRIVATE_KEY"]).address;
  await localFunctionsTestnetInfo.getFunds(
    addressToFund,
    {
      weiAmount: utils.parseEther("100").toString(), // 100 ETH
      juelsAmount: utils.parseEther("100").toString(), // 100 LINK
    }
  );

  if (process.env["SECOND_PRIVATE_KEY"]) {
    const secondAddressToFund: string = new Wallet(
      process.env["SECOND_PRIVATE_KEY"]
    ).address;
    await localFunctionsTestnetInfo.getFunds(
      secondAddressToFund,
      {
        weiAmount: utils.parseEther("100").toString(), // 100 ETH
        juelsAmount: utils.parseEther("100").toString(), // 100 LINK
      }
    );
  }

  // Update values in networks.js
  let networksConfig = fs.readFileSync(
    path.join(process.cwd(), "networks.js")
  ).toString();
  const regex = /localFunctionsTestnet:\s*{\s*([^{}]*)\s*}/s;
  const newContent = `localFunctionsTestnet: {
    url: "http://localhost:8545/",
    accounts,
    confirmations: 1,
    nativeCurrencySymbol: "ETH",
    linkToken: "${localFunctionsTestnetInfo.linkTokenContract.address}",
    functionsRouter: "${localFunctionsTestnetInfo.functionsRouterContract.address}",
    donId: "${localFunctionsTestnetInfo.donId}",
  }`;
  networksConfig = networksConfig.replace(regex, newContent);
  fs.writeFileSync(path.join(process.cwd(), "networks.js"), networksConfig);
})();
