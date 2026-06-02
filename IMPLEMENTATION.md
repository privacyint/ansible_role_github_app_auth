# Implementation guide: github_app_auth role

This document maps the requested plan to concrete repository changes and highlights remaining low-risk refinements.

## Delivered in this repository

- Role scaffolding and metadata:
  - `defaults/main.yml`
  - `tasks/main.yml`, `tasks/validate.yml`, `tasks/token.yml`, `tasks/checkout.yml`
  - `meta/main.yml`
- Helper script for JWT + installation token flow:
  - `files/github_app_token.py`
- Lint/test/CI scaffolding:
  - `.ansible-lint`, `molecule/default/*`, `.github/workflows/ci.yml`, `Makefile`, `requirements.txt`
- Governance and docs:
  - `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`

## Task-flow design

1. `tasks/validate.yml`
   - Asserts required vars are present.
   - Validates repository list items when checkout mode is enabled.
2. `tasks/token.yml`
   - Ensures private cache directory (`0700`).
   - Invokes `files/github_app_token.py` with strict args.
   - Parses JSON result and sets role facts with `no_log: true`.
3. `tasks/checkout.yml`
   - Uses `ansible.builtin.git` with a token-authenticated HTTPS URL.
   - Skips entirely if `github_app_auth_repositories` is empty.

## Helper script behaviour contract

Input arguments:

- `--app-id`
- `--installation-id`
- `--private-key-b64`
- `--api-url`
- `--ttl-seconds`
- `--refresh-buffer-seconds`
- `--cache-enabled`
- `--cache-file`

Output (stdout JSON):

- Success:
  - `token`
  - `expires_at`
  - `source` (`cache`|`fresh`)
- Failure:
  - `error`
  - non-zero exit code

## Security controls checklist

- [x] `no_log: true` on sensitive tasks.
- [x] Cache directory/file restricted (`0700` / `0600`).
- [x] Short-lived tokens and refresh buffer support.
- [x] No plaintext token writes in role tasks.
- [x] Placeholder-only `.env` added for local testing convenience.

## Suggested final refinements (small and optional)

1. Add explicit TLS/proxy controls for restricted networks.
2. Add retry/backoff around token exchange in helper script.
3. Extend Molecule tests with mocked HTTP responses for deterministic CI.
4. Add optional Key Vault lookup pattern examples in README.
5. Add role changelog + release tagging process.

## Manual rollout checklist

1. Run `make lint` and `make test`.
2. Confirm helper script executes on your target runners.
3. Validate token-only flow in Semaphore.
4. Validate one private repo checkout end-to-end.
5. Verify logs contain no key/JWT/token material.

## Cross-repo work intentionally excluded here

Per request, this repository does **not** include edits to:

- `/Users/chrisw/opentofu-pubcloud/requirements.yml`
- playbook integration points in other repositories

These should be straightforward after this role is pushed and pinned by commit SHA.
