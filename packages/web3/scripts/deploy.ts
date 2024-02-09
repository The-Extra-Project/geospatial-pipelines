import {ethers} from "hardhat";
import {CircumToken__factory, AccessControl__factory} from "../typechain-types"

export async function deployContracts() {
  const oracleAddress = '0x12AE66CDc592e10B60f9097a7b0D3C59fce29876';
  const evalDeploymentAddress = '0x12AE66CDc592e10B60f9097a7b0D3C59fce29876'; // done after deploying the address.
  const multiplicationFactor = "7"
  
  const ctFactory = await ethers.getContractFactory("CircumToken")
  const stakingContract = await ethers.getContractFactory("StakingContract")
  const ctContract  = await ctFactory.deploy(multiplicationFactor, oracleAddress,evalDeploymentAddress)

  await ctContract.waitForDeployment();
  console.log(
    `contract deployed with  address: ` + await ctContract.address
  );





}

deployContracts().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
