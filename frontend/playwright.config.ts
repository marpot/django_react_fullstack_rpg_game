import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  outputDir: "./node_modules/.cache/playwright-results",
  use: { baseURL: "http://127.0.0.1:3000" },
  webServer: {
    command: "npm run dev -- --no-open",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: !process.env.CI,
  },
});
