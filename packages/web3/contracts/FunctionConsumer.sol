// SPDX-License-Identifier: MIT

/// @title contract that takes the consumption of the offchain parameter values in order to call the onchain contract function
/// @author credits to the Functions Consumer contract format from the chainlink hardha template
/// @notice currently the contract is not secure in implementation and there needs to be a way to verify the function contract.

import {FunctionsClient} from "@chainlink/contracts/src/v0.8/functions/dev/v1_0_0/FunctionsClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import {FunctionsRequest} from "@chainlink/contracts/src/v0.8/functions/dev/v1_0_0/libraries/FunctionsRequest.sol";

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

contract FunctionConsumer is AccessControl, ConfirmedOwner, FunctionsClient {
    bytes32 public s_lastRequestId;
    bytes public s_lastResponse;
    bytes public s_lastError;
    bytes32 _donId;
    bytes32 constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    constructor(
        address router,
        bytes32 donId,
        address _admin
    ) FunctionsClient(router) ConfirmedOwner(msg.sender) {
        _donId = donId;
        grantRole(ADMIN_ROLE, _admin);
    }

    /**
     *
     * @notice setting donId based on the support on given chain
     * @param newDonId is the new id of the keeper infrastructure.
     */
    function setDonId(bytes32 newDonId) external {
        require(
            hasRole(ADMIN_ROLE, msg.sender),
            "FunctionConsumer: Sender must be admin"
        );
        _donId = newDonId;
    }

    /// @notice This function sets the function call to the circumToken as defined by the user
    /// @dev this has to be called buy the keeper held by the admin wallet.
    ///    @param source JavaScript source code
    ///   * @param secretsLocation Location of secrets (only Location.Remote & Location.DONHosted are supported)
    ////   * @param encryptedSecretsReference Reference pointing to encrypted secrets
    ////   * @param args String arguments passed into the source code and accessible via the global variable `args`
    ////   * @param bytesArgs Bytes arguments passed into the source code and accessible via the global variable `bytesArgs` as hex strings
    ////   * @param subscriptionId Subscription ID used to pay for request (FunctionsConsumer contract address must first be added to the subscription)
    ////   * @param callbackGasLimit Maximum amount of gas used to call the inherited `handleOracleFulfillment` method
    //// @return gives the requestId of the given function request.

    function sendFunctionRequest(
        string calldata source,
        FunctionsRequest.Location secretsLocation,
        bytes calldata encryptedSecretsReference,
        string[] calldata args,
        bytes[] calldata bytesArgs,
        uint64 subscriptionId,
        uint32 callbackGasLimit
    ) external returns (bytes32) {
        require(
            hasRole(ADMIN_ROLE, msg.sender),
            "sendFunctionRequests: Sender must be admin"
        );
        FunctionsRequest.Request memory req;
        req.initializeRequest(
            FunctionsRequest.Location.Inline,
            FunctionsRequest.CodeLanguage.JavaScript,
            source
        );
        req.secretsLocation = secretsLocation;
        req.encryptedSecretsReference = encryptedSecretsReference;

        if (args.length > 0) {
            req.setArgs(args);
        }
        if (bytesArgs.length > 0) {
            req.setBytesArgs(bytesArgs);
        }
        s_lastRequestId = _sendRequest(
            req.encodeCBOR(),
            subscriptionId,
            callbackGasLimit,
            _donId
        );

        return s_lastRequestId;
    }

    /**
     * @notice Store latest result/error
     * @param requestId The request ID, returned by sendRequest()
     * @param response Aggregated response from the user code
     * @param err Aggregated error from the user code or from the execution pipeline
     * Either response or error parameter will be set, but never both
     */
    function fulfillRequest(
        bytes32 requestId,
        bytes memory response,
        bytes memory err
    ) internal override {
        s_lastResponse = response;
        s_lastError = err;
    }
}
