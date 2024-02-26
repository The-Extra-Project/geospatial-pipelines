import { task } from 'hardhat/config';
import { network_params } from '../hardhat.config';
import { network } from 'hardhat';
import hre from 'hardhat';
task(
  'deploy-consumer',
  'deploys first the consumer contract and then sets the addresses and params'
)
  .addParam('network', 'The network to deploy to')
  .setAction(async (taskArgs: any) => {
    console.log(`Deploying FunctionssConsumer contract to ${network.name}`);
    const functionsRouter = network_params[taskArgs.network]['functionsRouter'];

    const donIdBytes32 = hre.ethers.utils.formatBytes32String(
      functionsRouter['donId']
    );

    console.log('\n__Compiling Contracts__');
    await run('compile');

    const overrides = {};
    // If specified, use the gas price from the network config instead of Ethers estimated price
    if (network_params[network.name].gasPrice) {
      overrides.gasPrice = network_params[network.name].gasPrice;
    }
    // If specified, use the nonce from the network config instead of automatically calculating it
    if (network_params[network.name].nonce) {
      overrides.nonce = network_params[network.name].nonce;
    }

    const consumerContractFactory = await ethers.getContractFactory(
      'FunctionsConsumer'
    );
    const consumerContract = await consumerContractFactory.deploy(
      functionsRouter,
      donIdBytes32,
      overrides
    );

    console.log(
      `\nWaiting ${
        network_params[network.name].confirmations
      } blocks for transaction ${
        consumerContract.deployTransaction.hash
      } to be confirmed...`
    );
    await consumerContract.deployTransaction.wait(
      network_params[network.name].confirmations
    );

    console.log(
      '\nDeployed FunctionsConsumer contract to:',
      consumerContract.address
    );

    if (network.name === 'localFunctionsTestnet') {
      return;
    }

    const verifyContract = taskArgs.verify;
    if (
      network.name !== 'localFunctionsTestnet' &&
      verifyContract &&
      !!networks[network.name].verifyApiKey &&
      networks[network.name].verifyApiKey !== 'UNSET'
    ) {
      try {
        console.log('\nVerifying contract...');
        await run('verify:verify', {
          address: consumerContract.address,
          constructorArguments: [functionsRouter, donIdBytes32],
        });
        console.log('Contract verified');
      } catch (error) {
        if (!error.message.includes('Already Verified')) {
          console.log(
            'Error verifying contract.  Ensure you are waiting for enough confirmation blocks, delete the build folder and try again.'
          );
          console.log(error);
        } else {
          console.log('Contract already verified');
        }
      }
    } else if (verifyContract && network.name !== 'localFunctionsTestnet') {
      console.log(
        '\nScanner API key is missing. Skipping contract verification...'
      );
    }

    console.log(
      `\nFunctionsConsumer contract deployed to ${consumerContract.address} on ${taskArgs.name}`
    );
  });
