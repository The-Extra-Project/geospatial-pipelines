// SPDX-License-Identifier: MIT
pragma solidity  ^0.8.9;  

interface IFunctionConsumer {

    //TODO: implement the following function in the FunctionConsumer contract in order to get the PointCloud and other parameters from given dataset.
    /// this will be used to fetch either the total denomination of which the part of the share that various other users 

    function calculatePointCloudContribution(address _dataCollateral, uint256 stakedAmount) external returns(uint256);  
} 