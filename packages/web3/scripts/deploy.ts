import { ethers } from 'hardhat';

let address_outputs: Map<string, string>;
export async function deployContracts() {
  // these are addresses that have to compute the results from the chainlink and keeper address correspondingly.
  const oracleAddress = '';
  const keeperAddress = '';
  const multiplicationFactor: any = 7;
  const ctFactory = await ethers.getContractFactory('CircumToken');
  const stakingContract = await ethers.getContractFactory(
    'DataCollateralVault'
  );

  const functionsConsumer = await ethers.getContractFactory()

  const ctContract = await ctFactory.deploy(
    multiplicationFactor,
    oracleAddress,
    keeperAddress
  );
  const stContract = await stakingContract.deploy(
    ctContract.address,
    oracleAddress
  );

  await ctContract.deployed();
  await stContract.deployed();
  console.log(`contract deployed with  address: ` + (await ctContract.address));

  address_outputs.set('CircumToken: ', ctContract.address);
  address_outputs.set('StakingContract: ', stContract.address);

  console.log('Address of token contract + ' + ctContract.address);
  return ctContract.address; //, stContract.address
}

deployContracts().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
