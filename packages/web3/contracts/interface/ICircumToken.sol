// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

struct IndividualContribution {
    uint clientContribution; // parameter that corresponds to the number of point clouds generated in the reconstructed model
    uint reallignmentParameter; // this is defined by the colmap for images in order to insure that whether the 
    }
    
interface ICircumToken is IERC20 {
    
    /**
     * @dev this function defines the parameters of token rewards calculation.
     * @dev only OWNER has permission (provided to the chainlink function).
     * @param _clientAddress is the dataset provider address.
     * @param _contribution is the parameter value that corresponds to the total contribution of their as well as protocol achievements.
     */
    
    function addIndividualContribution(address _clientAddress, IndividualContribution memory _contribution)  external returns(bool);

    function getIndividualContributions(address _address) external view returns(IndividualContribution memory);

    function getMintedToken(address _address) external view returns(uint256);

    function mintToken(address _clientAddress)  external returns(bool);

    




}