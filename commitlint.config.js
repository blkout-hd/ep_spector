// commitlint.config.js
// Enforces conventional commit format for SPECTOR project

module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Type must be one of the following
    "type-enum": [
      2,
      "always",
      [
        "feat",       // New feature
        "fix",        // Bug fix
        "security",   // Security fix
        "refactor",   // Code refactoring
        "docs",       // Documentation
        "test",       // Tests
        "ci",         // CI/CD
        "chore",      // Maintenance
        "revert",     // Revert commit
        "perf",       // Performance
        "style",      // Formatting
      ]
    ],
    // Subject line formatting
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"]],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "subject-max-length": [2, "always", 72],
    
    // Body formatting
    "body-leading-blank": [2, "always"],
    "body-max-line-length": [2, "always", 100],
    
    // Footer formatting
    "footer-leading-blank": [2, "always"],
    "footer-max-line-length": [2, "always", 100],
    
    // Header formatting
    "header-max-length": [2, "always", 100],
    
    // Scope formatting (optional but encouraged)
    "scope-empty": [0, "always"], // Not required but can be enabled
    "scope-case": [2, "always", "lower-case"],
  },
  
  // Help message shown when commit fails
  helpUrl: "https://www.conventionalcommits.org/",
  
  // Prompt for commit details (optional, for CLI usage)
  prompt: {
    questions: {
      type: {
        description: "Select the type of change you are committing",
      },
      scope: {
        description: "What is the scope of this change (e.g., src, agents, mcp_servers)",
      },
      subject: {
        description: "Write a short, imperative tense description of the change",
      },
      body: {
        description: "Provide a longer description of the change",
      },
      isBreaking: {
        description: "Are there any breaking changes?",
      },
    },
  },
};
