## @geospatial-pipelines/storage

This package consist of the scripts for user to manage their storage on IPFS / filecoin on top of centralised gateway providers like [lighthouse](https://lighthouse.storage) or [web3.storage](https://web3.storage). it consist of the wrapper methods on top of the lighthouse API and server for the applications to interact with the application method. 


## Build instructions:

1. Define the .env file where you want to store the enviornment variables:
 - LIGHTHOUSE_KEY: api key generated with the lighthouse storage
 - PRIV_KEY : is the private key of the wallet on which you want to implement the storage. 
    - NOTE: you should NOT pass ever value as input to the LighthouseAPI and the library is not available for the production purposes, but we are going in future to integrate the wallet authentification provider.
 - ALCHEMY_KEY: in order to integrate the provider api


2. build the package using `npm run build` command

3. And then run the server command by running 'npm run server'.


## API

1. /login : takes input the public key of the wallet in order to login the user.
2. /upload: takes in the path of the file that you want to store encrypted
 