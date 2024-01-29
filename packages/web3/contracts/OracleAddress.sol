import {ChainlinkClient} from "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import {Chainlink} from "@chainlink/contracts/src/v0.8/Chainlink.sol";


contract OracleAddress is ChainlinkClient, ConfirmedOwner {
    
    address constant CHAINLINK_TOKEN_CONTRACT = "0x326C977E6efc84E512bB9C30f76E30c160eD06FB"; // for MUMBAI NETWORK
    address constant CHAINLINK_ORACLE_CONTRACT = "0x40193c8518BB267228Fc409a613bDbD8eC5a97b3";
    uint256 public volume;
    bytes32 private jobId;
    uint256 private fee;

    using Chainlink for Chainlink.Request;

    constructor() ConfirmedOwner(msg.sender) {
        setChainlinkToken(CHAINLIK_TOKEN_CONTRACT);
        setChainlinkOracle(CHAINLINK_ORACLE_CONTRACT);
        jobId = "" ; // this you can get by hosting the docker deployment from https://hub.docker.com/r/smartcontract/chainlink/tags and putting the parameters in the cron jobs
    }
    
    function  requestContributionStatistic() returns () {
        
    }




}