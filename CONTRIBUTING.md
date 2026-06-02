# Contributing

Thanks for contributing.

## Development setup

1. Use Python 3.10+.
2. Install dependencies from `requirements.txt`.
3. Run `make lint` and `make test` before submitting changes.

## Standards

- Use concise British English in docs.
- Avoid logging secrets.
- Prefer deterministic, idempotent automation.
- Keep role variable names explicit and prefixed (`github_app_auth_*`).

## Pull requests

- Include a clear summary of behaviour changes.
- Add or update Molecule coverage where behaviour changes.
- Confirm no secrets are introduced in fixtures, docs, or logs.
