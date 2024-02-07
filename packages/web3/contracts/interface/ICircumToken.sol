// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;


struct IndividualContribution {
    uint clientContribution; // parameter that corresponds to the number of point clouds generated in the reconstructed model
    uint reallignmentParameter; // this is defined by the colmap for images in order to insure that whether the 
    }
    
interface ICircumToken {
    function addIndividualContribution(address _clientAddress, IndividualContribution memory _contribution)  external returns(bool);


    function getIndividualContributions(address _address) external view returns(IndividualContribution memory);

    function getMintedToken(address _address) external view returns(uint256);

    function mintToken(address _clientAddress)  external returns(bool);






}