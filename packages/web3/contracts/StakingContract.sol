// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ICircumToken} from "./interface/ICircumToken.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ICircumToken} from "./interface/ICircumToken.sol";
import {IFunctionConsumer} from "./interface/IFunctionConsumer.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * contract for the users to stake tokens on the  given dataset .
 * only the dataset owners can get rewards proportional to the staked amount.
 *
 *
 *
 */
contract DataCollateralVault is ERC20 {
    event DataCollateralStaked(
        uint indexed dataProviderId,
        uint256 amount,
        address stakingUser,
        uint256 shares
    );
    

    event DatasetStored(
        uint indexed dataProviderId,
        address datasetOwner 
    );


    using Math for uint256;
    address dataToken;
    address _oracleAddress;
    ICircumToken rewardToken;
    mapping(uint256 => mapping(address => uint256)) public _stakedShares; // mapping of datasetId => tokenHolder => stakedAmount
    uint public _totalCollateralAmount;

    uint[] public datasetIds;
    mapping(uint => address) public datasetOwners;

    constructor(
        address _dataCollateral,
        address oracleAddress
    ) ERC20("DataVaultToken", "DVT") {
        dataToken = _dataCollateral;
        _oracleAddress = oracleAddress;
        rewardToken = ICircumToken(_dataCollateral);
    }

    function stakeToken(
        uint ipfs_dataset_id,
        uint tokenAmount
    ) public returns (uint256) {


        rewardToken.transferFrom(msg.sender, address(this), tokenAmount);

        _totalCollateralAmount += tokenAmount;

        uint256 shares = _convertToShares(tokenAmount, Math.Rounding.Floor);

        _stakedShares[ipfs_dataset_id][msg.sender] += shares;

        _mint(msg.sender, shares);

        emit DataCollateralStaked(
            ipfs_dataset_id,
            tokenAmount,
            msg.sender,
            shares
        );
        return shares;
    }


    function withdrawStakedToken(
        uint ipfs_dataset_id,
        uint256 shares
    ) public returns (uint256) {
        uint256 tokenAmount = _convertToShares(shares, Math.Rounding.Ceil);
        require(_stakedShares[ipfs_dataset_id][msg.sender] >= shares, "StakingContract:withdrawStakedToken: cant withdraw more than whats is defined");       
        _stakedShares[ipfs_dataset_id][msg.sender] -= shares;
        rewardToken.transferFrom(address(this), msg.sender, tokenAmount);
        _burn(msg.sender, shares);   
        return tokenAmount;
    }

    /**
     * this function allows the dataset owner to withdraw the rewards based on the reward its earning proportional to the staked amount by the other users
     * @param ipfs_dataset_id is the dataset id whose owner needs to get the rewards
     * @param _providers is the list of the addresses that havce staked the tokens for given dataset and the owner wants to withdraw.
     * 
     */
    function withdrawRewards(uint ipfs_dataset_id, address[] memory _providers) public  {
        require(msg.sender == datasetOwners[ipfs_dataset_id], "StakingContract:withdrawRewards: only the dataset owner can withdraw the rewards");

        uint totalStaked = 0;
        for (uint i = 0; i < _providers.length; i++) {
           totalStaked += _stakedShares[ipfs_dataset_id][_providers[i]];
           _transfer(address(this), msg.sender, _stakedShares[ipfs_dataset_id][_providers[i]] );
            }
            
            
            uint256 rewardAmount = _convertToShares(totalStaked, Math.Rounding.Floor);
            rewardToken.transferFrom(address(this), msg.sender, rewardAmount);
            

    }

    function _convertToShares(
        uint256 _rewardTokenStaked,
        Math.Rounding rounding
    ) internal view returns (uint256) {
        uint denominator = _totalCollateralAmount;
        require(denominator != 0, "invalid denominator");
        uint shares = _rewardTokenStaked.mulDiv(
            totalSupply() + 10 ** decimals(),
            denominator,
            rounding   
        ); // need to rectify in later versions
        return shares;
    }

    /// @notice this function is overloaded version of the ERC4626 contract to compute shares based on the already available data tokens for the given region of the contract
    /// @dev this will call internally the chainlink function to determine the share of data that is contributed by the given user.
    /// @param tokenAmount is the amount of the token that user is gonna staked and convert them to tokens
    /// @return the corresponding staking power the user will get if staking in the given vault

    function convertToShares(uint256 tokenAmount) public view returns (uint256) {
        return _convertToShares(tokenAmount, Math.Rounding.Ceil);
    }
}
