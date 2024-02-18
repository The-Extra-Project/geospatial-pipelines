import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-ethers"
import { SolcConfig } from "hardhat/types";
import "@nomicfoundation/hardhat-verify";
import {configDotenv} from "dotenv"

configDotenv(
  {
    path: '.env'

  }
)
// taking description from the chainlink hardhat function template deployments.
const accounts: any[] = []
const DEFAULT_VERIFICATION_BLOCK_CONFIRMATIONS = 2

export const network_params =  {

  polygon: {
    url: process.env.POLYGON_RPC_URL || "UNSET",
    gasPrice: undefined,
    nonce: undefined,
    accounts,
    verifyApiKey: process.env.POLYGONSCAN_API_KEY || "UNSET",
    chainId: 137,
    confirmations: DEFAULT_VERIFICATION_BLOCK_CONFIRMATIONS,
    nativeCurrencySymbol: "ETH",
    linkToken: "0xb0897686c545045aFc77CF20eC7A532E3120E0F1",
    linkPriceFeed: "0x5787BefDc0ECd210Dfa948264631CD53E68F7802", // LINK/MATIC
    functionsRouter: "0xdc2AAF042Aeff2E68B3e8E33F19e4B9fA7C73F10",
    donId: "fun-polygon-mainnet-1",
    gatewayUrls: ["https://01.functions-gateway.chain.link/", "https://02.functions-gateway.chain.link/"],
  },
  polygonMumbai: {
    url: process.env.POLYGON_MUMBAI_RPC_URL || "UNSET",
    gasPrice: 20_000_000_000,
    nonce: undefined,
    accounts,
    verifyApiKey: process.env.POLYGONSCAN_API_KEY || "UNSET",
    chainId: 80001,
    confirmations: 10,
    nativeCurrencySymbol: "MATIC",
    linkToken: "0x326C977E6efc84E512bB9C30f76E30c160eD06FB",
    linkPriceFeed: "0x12162c3E810393dEC01362aBf156D7ecf6159528", // LINK/MATIC
    functionsRouter: "0x6E2dc0F9DB014aE19888F539E59285D2Ea04244C",
    donId: "fun-polygon-mumbai-1",
    gatewayUrls: [
      "https://01.functions-gateway.testnet.chain.link/",
      "https://02.functions-gateway.testnet.chain.link/",
    ],
  },

  
  // localFunctionsTestnet is updated dynamically by scripts/startLocalFunctionsTestnet.js so it should not be modified here
  localFunctionsTestnet: {
    url: "http://localhost:8545/",
    accounts,
    confirmations: 1,
    nativeCurrencySymbol: "ETH",
    linkToken: "0x9E9f0eFcdDA5e7c0850b643FEb5F5D23D5E85B44",
    functionsRouter: "0x99125A5Ba0B1F8CC2E440256B4A1839D61B99e52",
    donId: "local-functions-testnet",
  },
}

const config: HardhatUserConfig | SolcConfig = {
  solidity: "0.8.24",

  networks: {
    ...network_params
  },
  settings: {
    viaIR: true
  },

  etherscan: {
    apiKey: process.env.POLYGONSCAN_API_KEY || ''
  },
  sourcify: {
    enabled: true
  },

  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }

  
};



export default config;
