import express, { Application, Request, Response, Express } from 'express';
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

// enter the public key of the wallet registered.
let storage = new LighthouseStorageAPI("devextralabs", "", provider, process.env.API_KEY)


app.use((err: Error, req: Request, res: Response, next: () => void) => {
  console.error('corresponding issue:' + err.name + ' issue: ' + err.message);

});


app.get('/', (req, res) => {
  res.send('extralabs storage API')
})

app.use(bodyParser.json());


app.post('/upload', async (req: Request, res: Response) => {
  try {
    const { filepath }: { filepath: string } = req.body; // Type checking for body
    const cid = await storage.uploadDatasetEncrypted(filepath);
    res.json({ Hash: cid });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "/upload status: 500" });
  }
})



app.get('/decrypt/:cid/:publicKey/:filename_path', async (req: Request, res: Response) => {
  try {
    const { cid, publicKey, filename_path } = req.params; // Type checking for params
    await await storage.decryptFile(cid, publicKey, filename_path);
    res.json({ message: 'File decrypted and saved successfully.' });
  } catch (err: any) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});


app.listen(port, () => console.log(`App listening on PORT ${port}`))