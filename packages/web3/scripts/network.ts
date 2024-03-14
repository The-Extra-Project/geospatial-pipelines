import config from "@chainlink/env-enc"

let env_vars = config('../.env.enc')

const DEFAULT_VERIFICATION_BLOCK_CONFIRMATIONS = 2

const npmCommand = env_vars.npm_lifecycle_event
const isTestEnvironment = npmCommand == "test" || npmCommand == "test:unit"
const isSimulation = process.argv.length === 3 && process.argv[2] === "functions-simulate-script" ? true : false


// Set EVM private keys (required)
const PRIVATE_KEY = process.env.PRIVATE_KEY


if (!isTestEnvironment && !isSimulation && !PRIVATE_KEY) {
    throw Error("Set the PRIVATE_KEY environment variable with your EVM wallet private key")
  }
  
  const accounts = []
  if (PRIVATE_KEY) {
    accounts.push(PRIVATE_KEY)
    }



