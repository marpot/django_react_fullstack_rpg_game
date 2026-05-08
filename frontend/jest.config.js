/** @type {import('jest').Config} */
const config = {
  // Automatically clear mock calls, instances, contexts, and results before each test
  clearMocks: true,

  // Collect coverage information while executing the test
  collectCoverage: true,

  // Directory where Jest should output its coverage files
  coverageDirectory: "coverage",

  // Transform files with Babel before testing
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },

  // Specify the test environment
  testEnvironment: 'jsdom',

  // Ignore transformation for node_modules
  transformIgnorePatterns: [
    '/node_modules/',
  ],

  // File extensions Jest will recognize
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],
};

module.exports = config;
