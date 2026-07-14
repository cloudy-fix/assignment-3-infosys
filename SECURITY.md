# Security Policy

## Supported Use

This repository is maintained as a portfolio project. Security fixes should prioritize safe defaults, secret management, dependency hygiene, and clear operational documentation.

## Reporting Issues

If you find a security problem, do not open a public issue with secrets or exploit details. Contact the maintainer privately through the portfolio or LinkedIn profile.

## Secret Handling

- Do not commit .env, API keys, passwords, tokens, private keys, certificates, generated databases, or local dependency folders.
- Use .env.example for safe sample configuration.
- Rotate any credential that was ever committed before using the project in production.
