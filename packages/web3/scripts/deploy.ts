import { ethers } from 'hardhat';

let address_outputs: Map<string, string>;
export async function deployContracts() {
  const oracleAddress = '0x36E8895442C8D90419a0a791D117339B78CbB656';
  const keeperAddress = '0x36E8895442C8D90419a0a791D117339B78CbB656';
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
