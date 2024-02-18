## @geospatial-pipeline/web3

Tokenization and transfer to the clienbt based on the contribution of the data to the protocol.


### chainlink-functions/:

Off-chain service that calculates the contribution metrics of each data provider . this metric will be then provided as data feed for the smart contracts (as an oracle) or any other frontend service in order to categorise the various data providers. 

It short: It takes parameters from the geospatial reconstruction pipeline and then calculates the result as the (total data parameters contributed by the data providers - the amount of effort being put by the extralabs curators in order to calibrate the data further in order to reconstruct it).

## Build service