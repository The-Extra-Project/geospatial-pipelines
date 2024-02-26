// SPDX-License-Identifier: MIT 

pragma solidity ^0.8.5;
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import "./interface/ICircumToken.sol";

contract CircumToken is ERC20, AccessControl {
    mapping (address=>uint256) tokenMinted;
    mapping(address => IndividualContribution) contributionMetrics;

    event IndividualContributionAdded(address indexed _clientAddresss);
    event TokenMinted(address indexed _address, uint amount);
    uint  tokenMultiplier; // this is the parameter (natural number decided by admin) that is multiplied with the total contribution score in order to generate the renumeration of the token.
    address oracleAddress;
    address keeperAddress; // address of the keeper bot (that essentially calls the mint function as soon as the results of the reconstruction are generated).
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE"); // attributed to the admin to transfer the token from the user.
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    constructor(uint _tokenMultiplier, address _oracleAddress, address _keeperAddress) ERC20("circumToken", "CT") {
        tokenMultiplier = _tokenMultiplier;
        oracleAddress = _oracleAddress;
        keeperAddress = _keeperAddress;
        _grantRole(MINTER_ROLE, _keeperAddress);
        _grantRole(ORACLE_ROLE, oracleAddress);
    }

    function addIndividualContribution(address _clientAddress, IndividualContribution memory _contribution)  public returns(bool) {
        assert(_clientAddress != address(0) && hasRole(ORACLE_ROLE, msg.sender) );
        contributionMetrics[_clientAddress] = _contribution;
        emit IndividualContributionAdded(_clientAddress);
        return true;
    }

    function getIndividualContributions(address _address) public view returns(IndividualContribution memory) {
        return(contributionMetrics[_address]);
    }

    function getMintedToken(address _address) public view returns(uint256) {
        assert(msg.sender != address(0));
        return(tokenMinted[_address]);
    }

    function mintToken(address _clientAddress)  public returns(bool) {
        assert(_clientAddress != address(0) && hasRole(MINTER_ROLE, msg.sender) && contributionMetrics[_clientAddress].clientContribution > contributionMetrics[_clientAddress].reallignmentParameter );
        uint tokenToBeMinted =  contributionMetrics[_clientAddress].clientContribution - (tokenMultiplier * contributionMetrics[_clientAddress].reallignmentParameter );
        _mint(_clientAddress, tokenToBeMinted);
        tokenMinted[_clientAddress] += tokenToBeMinted;
        emit TokenMinted(_clientAddress, tokenToBeMinted);
        return true;

    }
 
}