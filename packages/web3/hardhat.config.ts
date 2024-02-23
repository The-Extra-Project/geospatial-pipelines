import { HardhatUserConfig } from "hardhat/config";
import { SolcConfig } from "hardhat/types";
import "@nomicfoundation/hardhat-verify";
import "@typechain/hardhat";
import { configDotenv } from "dotenv";

configDotenv()

const accounts: any[] = [`${process.env.PRIVATE_KEY}`]
const DEFAULT_VERIFICATION_BLOCK_CONFIRMATIONS = 2

export const network_params =  {

  polygon: {
    url: process.env.POLYGON_RPC_URL || "UNSET",
    accounts,
    verifyApiKey: process.env.POLYGONSCAN_API_KEY || "UNSET",
    chainId: 137,
    confirmations: DEFAULT_VERIFICATION_BLOCK_CONFIRMATIONS,
    nativeCurrencySymbol: "ETH",
    linkToken: "0xb0897686c545045aFc77CF20eC7A532E3120E0F1",
    linkPriceFeed: "0x5787BefDc0ECd210Dfa948264631CD53E68F7802", // LINK/MATIC
    functionsRouter: "0xdc2AAF042Aeff2E68B3e8E33F19e4B9fA7C73F10",
    donId: "fun-polygon-mainnet-1",
    gatewayUrls: ["https://01.functions-gateway.chain.link/", "https://02.functions-gateway.chain.link/"]
  },
  polygonMumbai: {
    url: process.env.POLYGON_MUMBAI_RPC_URL || "UNSET",
    gasPrice: 20_000_000_000,
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
  typechain: {
    outDir: 'scripts/typechain-types',
    target: 'ethers-v6',
    alwaysGenerateOverloads: false, // should overloads with full signatures like deposit(uint256) be generated always, even if there are no overloads?
    externalArtifacts: ['externalArtifacts/*.json'], // optional array of glob patterns with external artifacts to process (for example external libs from node_modules)
    dontOverrideCompile: false // defaults to false

  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }

  
};



// task("wallet", "runs the cometh wallet abstraction", async(amount, hre) => {
//   //let wallet = new ethers.Wallet()
//   const tokenAddress = "0x66fd19Dcd8a8A144415b5C2274B6dD737f639B7B"
//   const oracleAddress = "0x36E8895442C8D90419a0a791D117339B78CbB656"
//   let  sessionToken : Map<string,string> = new Map()
//   // demo integration of the oauth provider and the corresponding token (ONLY for test purposes)
//   sessionToken.set("0x36E8895442C8D90419a0a791D117339B78CbB656","testAuth")
//   let abstractToken = new AbstractedWalletCometh(SupportedNetworks.MUMBAI, sessionToken, tokenAddress)
//   console.log("wallet getting connected w/ params", )
//   console.log("wallet initialized with address: " + await abstractToken.wallet.getAddress() + ":" + await abstractToken.wallet.getOwners())
  

//   const parameter_vars: IndividualContributionStruct = {
//     clientContribution: "90",
//     reallignmentParameter: "10"
//   }
//   await abstractToken.addIndividualContribution(oracleAddress, parameter_vars)
//   //await abstractToken.mintTokenAddress(oracleAddress) 
 
// })

export default config;
