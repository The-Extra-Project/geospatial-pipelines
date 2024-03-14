import express from "express";
const logger = require("morgan");
import * as path from "path";

import { errorHandler, errorNotFoundHandler } from "@web3/server/middlewares/errorHandling";

// Routes
import { run_compute_params } from "@web3/server/controller/index";
// Create Express server
export const app = express();

// Express configuration
app.set("port", process.env.PORT || 3000);
app.set("views", path.join(__dirname, "../views"));
app.set("view engine", "pug");

app.use(logger("dev"));


app.use("/web3", run_compute_params);

app.use(errorNotFoundHandler);
app.use(errorHandler);