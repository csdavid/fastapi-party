const { defineConfig } = require("cypress");

module.exports = defineConfig({
  video: true,
  screenshotsFolder: 'cypress/screenshots',
  videosFolder: 'cypress/videos',
  e2e: {
    baseUrl: 'http://127.0.0.1:8000/',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
