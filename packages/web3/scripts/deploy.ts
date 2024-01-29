import { ethers } from "hardhat";
async function main() {
  const oracleAddress = '0x12AE66CDc592e10B60f9097a7b0D3C59fce29876';
  const evalDeploymentAddress = '0x12AE66CDc592e10B60f9097a7b0D3C59fce29876'; // done after deploying the address.
  const multiplicationFactor = "7"
  const ctContract = await ethers.deployContract("CircumToken", [multiplicationFactor,oracleAddress, evalDeploymentAddress]);
   
  // getting contract factory
  //let ctContractFactory = ethers.getContractFactory()


  await ctContract.waitForDeployment();

  console.log(
    `contract deployed with  address: ` + await ctContract.getAddress()
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
