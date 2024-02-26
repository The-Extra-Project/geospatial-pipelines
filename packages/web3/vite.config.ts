import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    resolve: { alias: { chainlink_functions: resolve('chainlink-functions/') } },
  })
  