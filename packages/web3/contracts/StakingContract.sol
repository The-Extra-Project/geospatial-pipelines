// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;


import {ERC4626} from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ICircumToken} from "./interface/ICircumToken.sol";
import {IFunctionConsumer} from "./interface/IFunctionConsumer.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {AccessControl} from "@openzeppelin/contracts/utils/access/AccessControl.sol";


contract DataCollateralVault is ERC4626 {
    using Math for uint256;
    address dataCollateral;
    address _oracleAddress;
    mapping()
    constructor(address _dataCollateral,address oracleAddress) ERC4626(IERC20(_dataCollateral)) {
        dataCollateral = _dataCollateral;
        _oracleAddress = oracleAddress;

    }

function _convertToShares(uint256 _shares) private  returns(uint256) {
    uint denominator = IFunctionConsumer(_oracleAddress).calculatePointCloudContribution(dataCollateral, _shares);
    //TODO to be tested with the several assumptions.
    require(denominator != 0, "invalid denominator");
    uint shares = Math.mulDiv( _shares, 10 , denominator ); // need to rectify in later versions
    return shares;
}
    /// @notice this function is overloaded version of the ERC4626 contract to compute shares based on the already available data tokens for the given region of the contract
    /// @dev this will call internally the chainlink function to determine the share of data that is contributed by the given user.
    /// @param tokenAmount is the amount of the token that user is gonna staked and convert them to tokens
    /// @return the corresponding staking power the user will get if staking in the given vault
function convertToShares(uint256 tokenAmount) public virtual view override(ERC4626) returns(uint256) {
    return _convertToShares(tokenAmount);
}

}




