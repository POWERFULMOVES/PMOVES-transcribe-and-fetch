const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  // Only look for tests in the src directory
  roots: ['<rootDir>/src'],
  // Alternatively, use testMatch to specify test file patterns within src
  // testMatch: ['<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}', '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}'],
  moduleNameMapper: {
    // Ensure correct paths and remove duplicates
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/app/(.*)$': '<rootDir>/src/app/$1',
    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',
    // Mock problematic ESM modules
    '^react-markdown$': '<rootDir>/__mocks__/react-markdown.js',
    // Add other mappings if necessary
  },
  testEnvironment: 'jest-environment-jsdom',
  // Ignore docs and other non-src directories for module resolution and test discovery
  modulePathIgnorePatterns: [
    '<rootDir>/docs/',
    '<rootDir>/pipecatdocs/',
    '<rootDir>/backend/',
    '<rootDir>/pmoves-agent-registry/',
    '<rootDir>/pmoves-pipecat/',
    '<rootDir>/pmoves-pipecat-agent/',
    '<rootDir>/supabase-agent/',
    '<rootDir>/monitoring/',
    '<rootDir>/deployment/',
    '<rootDir>/litellm_proxy_config/',
    '<rootDir>/migrations/'
  ],
  watchPathIgnorePatterns: [
    '<rootDir>/docs/',
    '<rootDir>/pipecatdocs/',
    '<rootDir>/backend/',
    '<rootDir>/pmoves-agent-registry/',
    '<rootDir>/pmoves-pipecat/',
    '<rootDir>/pmoves-pipecat-agent/',
    '<rootDir>/supabase-agent/',
    '<rootDir>/monitoring/',
    '<rootDir>/deployment/',
    '<rootDir>/litellm_proxy_config/',
    '<rootDir>/migrations/'
  ],
  // More comprehensive transformIgnorePatterns for ESM modules
  transformIgnorePatterns: [
    // Transform all ESM packages that might be used
    '/node_modules/(?!(react-markdown|remark-parse|remark-rehype|unified|mdast-util-from-markdown|micromark|mdast-util-to-string|unist-util-stringify-position|vfile|vfile-message|bail|trough|remark-rehype|hast-util-raw|space-separated-tokens|property-information|hast-util-to-jsx-runtime|unist-util-visit|unist-util-is|mdast-util-to-hast|mdast-util-definitions|decode-named-character-reference|character-entities|ccount|escape-string-regexp|is-plain-obj|longest-streak|markdown-table|zwitch|micromark-util-chunked|micromark-util-classify-character|micromark-util-resolve-all|micromark-util-sanitize-uri|micromark-util-subtokenize|micromark-util-symbol|micromark-util-types|micromark-util-combine-extensions|micromark-util-character|micromark-util-decode-numeric-character-reference|micromark-util-decode-string|micromark-util-normalize-identifier|micromark-util-html-tag-name|micromark-factory-space|micromark-factory-whitespace|micromark-core-commonmark|mdast-util-to-markdown|mdast-util-to-string|unist-builder|unist-util-generated|unist-util-position|unist-util-visit-parents|vfile-location|vfile-sort|vfile-statistics|hast-to-hyperscript|hast-util-from-parse5|hast-util-parse-selector|hast-util-whitespace|web-namespaces|zwitch|comma-separated-tokens|hastscript|style-to-object|inline-style-parser|is-alphabetical|is-alphanumerical|is-decimal|is-hexadecimal|is-whitespace-character|is-word-character|mdast-util-to-hast|mdast-util-to-string|micromark-extension-gfm|micromark-extension-gfm-autolink-literal|micromark-extension-gfm-footnote|micromark-extension-gfm-strikethrough|micromark-extension-gfm-table|micromark-extension-gfm-tagfilter|micromark-extension-gfm-task-list-item|remark-gfm|remark-parse|remark-rehype|unified|unist-util-is|unist-util-remove-position|unist-util-visit|vfile|vfile-message)/)',
  ],
  // Explicitly define transform for JS/JSX
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
