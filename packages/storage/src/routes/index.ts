import { Router } from "express";

import * as controller from "../controllers/server"


export const index = Router();


index.get("/",  controller.index)
index.get("/upload", controller.upload)
index.get("/download/", controller.download_file)
