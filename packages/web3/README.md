## @dev-extralabs/web3

Package for handling operations onchain for the circum protocol. this includes:

1. Deployment and operations over smart contracts.
2. Wallet abstraction and transaction Management (created for every creation of the account by the user). 

### chainlink-functions/:

Off-chain service that calculates the contribution metrics of each data provider . this metric will be then provided as data feed for the smart contracts (as an oracle) or any other frontend service in order to categorise the various data providers. 

It short: It takes parameters from the geospatial reconstruction pipeline and then calculates the result as the (total data parameters contributed by the data providers - the amount of effort being put by the extralabs curators in order to calibrate the data further in order to reconstruct it).

## Build:

## import 
1. install the package via npm: `npm install @geospatial-pipeline/web3`
2. setup account with cometh and then set the enviornment vairable: `export COMETH_API_KEY=""`
   - Similarly for the alchemy for fetching the transaction data of blockchain.
3. then you can import the script in another node project for the following usecases
    - [cometh wallet integration](): you can  use the methods defined in the 
        - `scripts/cometh-api.ts` in order to integrate the wallet purely in the backend (examples shown below).  
        - `scritps/abstraction.ts` which is used for interacting with the token contract in frontend.
    
    - []