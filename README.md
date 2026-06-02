# ansible_role_github_app_auth

An Ansible role to authenticate with GitHub Apps, cache installation tokens safely, and optionally checkout private repositories over HTTPS.

This role supports two modes:

1. **Token-only mode**: request/cache a GitHub App installation token and expose Ansible facts.
2. **Token + checkout mode**: use that token to clone/update private repositories.

## Why this role exists

CI/CD systems such as Semaphore often need short-lived credentials to access private GitHub repositories. GitHub App installation tokens are short-lived, auditable, and safer than long-lived PATs.

## Requirements

- Ansible >= 2.14
- Python 3.10+
- Python packages:
  - `PyJWT`
  - `requests`

Install dev/test dependencies:

- `make lint`
- `make test`

## Variables

### Required inputs

- `github_app_id` (string)
- `github_installation_id` (string)
- `github_private_key_b64` (string, base64-encoded PEM private key)

### Optional behaviour

- `github_app_auth_api_url` (default: `https://api.github.com`)
- `github_app_auth_base_url` (default: `https://github.com`)
- `github_app_auth_cache_enabled` (default: `true`)
- `github_app_auth_cache_dir` (default: `/tmp/github_app_auth`)
- `github_app_auth_cache_file` (default: `{{ github_app_auth_cache_dir }}/installation_token.json`)
- `github_app_auth_refresh_buffer_seconds` (default: `300`)
- `github_app_auth_repositories` (default: `[]`)

### Output facts

- `github_app_auth_token`
- `github_app_auth_token_expires_at`
- `github_app_auth_token_source` (`cache` or `fresh`)
- `github_app_auth_headers`

## Usage

Full runnable playbooks are available in `examples/`:

- `examples/token_only.yml`
- `examples/checkout_single_repo.yml`
- `examples/checkout_multiple_repos.yml`

See `examples/README.md` for quick run instructions.

### Token-only mode

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: github_app_auth
      vars:
        github_app_id: "{{ lookup('env', 'GITHUB_APP_ID') }}"
        github_installation_id: "{{ lookup('env', 'GITHUB_INSTALLATION_ID') }}"
        github_private_key_b64: "{{ lookup('env', 'GITHUB_PRIVATE_KEY_B64') }}"
```

### Token + checkout mode

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: github_app_auth
      vars:
        github_app_id: "{{ lookup('env', 'GITHUB_APP_ID') }}"
        github_installation_id: "{{ lookup('env', 'GITHUB_INSTALLATION_ID') }}"
        github_private_key_b64: "{{ lookup('env', 'GITHUB_PRIVATE_KEY_B64') }}"
        github_app_auth_repositories:
          - repo: "privacyint/private-module-a"
            dest: "/tmp/private-module-a"
            version: "main"
            update: true
```

## Semaphore notes

Suggested environment variables:

- `GITHUB_APP_ID`
- `GITHUB_INSTALLATION_ID`
- `GITHUB_PRIVATE_KEY_B64`

To convert a PEM key to base64 safely:

```bash
base64 -i github_app_private_key.pem | tr -d '\n'
```

## Security model

- Secrets are never logged from token-generation tasks (`no_log: true`).
- Cache directory is created with mode `0700`.
- Cache file is written with mode `0600`.
- Token refresh happens before expiry using `github_app_auth_refresh_buffer_seconds`.

## Local verification

- `make lint`
- `make test`

## Implementation status

This repository now includes a concrete starter implementation and a detailed implementation guide in `IMPLEMENTATION.md` for any final hardening/refinement.
