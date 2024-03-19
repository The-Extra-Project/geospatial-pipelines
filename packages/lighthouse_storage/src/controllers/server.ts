import express, {  Request, Response, Express } from 'express';
import bodyParser from 'body-parser';
import ethers from "ethers"
import { providers } from "ethers"
import { config } from 'dotenv';


config({
  path: '../.env'
})

import { LighthouseStorageAPI } from "../Storage";


let provider = new providers.AlchemyProvider("maticmum", process.env.ALCHEMY_API_KEY)

let app = express()
let port = process.env.PORT || 3000;

let web3_storage_key = ""
export const login = app.use('/login', async (req: Request, res: Response)  => {
const public_key: string = req.body
// enter the public key of the wallet registered.
web3_storage_key = public_key
res.json({message: "public key account holder " + public_key + " is loggedin"})
});



let storage = new LighthouseStorageAPI("devextralabs",web3_storage_key, provider, process.env.API_KEY)

export const index = app.get('/', (req, res) => {
  res.send('extralabs storage API')
})


export const upload = async (req: Request, res: Response): Promise<void> => {
  try {
    const filepath : string  = req.body; // Type checking for body
    const cid = await storage.uploadDatasetEncrypted(filepath);
    res.json({ Hash: cid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "/upload status: 500" });
  }
}

export const download_file = async (req: Request, res: Response): Promise<void> => {
  try {
    const { cid, publicKey, filename_path } = req.params; // Type checking for params
    await await storage.decryptFile(cid, publicKey, filename_path);
    res.json({ message: 'File decrypted and saved successfully.' });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
};


app.listen(port, () => console.log(`App listening on PORT ${port}`))