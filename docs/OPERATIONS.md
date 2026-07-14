# Operations Guide

## Local Setup

1. Review README.md for the project goal and stack.
2. Copy .env.example to .env if the project needs runtime configuration.
3. Install dependencies using the stack-specific manifest when present.
4. Run the app or script through the command documented in the README.

## Configuration

- Never commit real .env files, API keys, tokens, passwords, generated databases, or virtual environments.
- Keep sample values in .env.example descriptive and safe.
- Prefer environment variables for URLs, credentials, feature flags, and runtime settings.

## Release Checklist

- git status --short shows only intended changes.
- GitHub Actions CI passes.
- Architecture and workflow diagrams are current.
- README, SECURITY, and CONTRIBUTING files are aligned with the latest project behavior.
