# Example playbooks

These playbooks demonstrate common usage patterns for `github_app_auth`.

## Prerequisites

Export the required environment variables (placeholder values shown):

- `GITHUB_APP_ID`
- `GITHUB_INSTALLATION_ID`
- `GITHUB_PRIVATE_KEY_B64`

## Playbooks

- `token_only.yml` — acquire/cache token and expose role facts.
- `checkout_single_repo.yml` — acquire token and checkout one private repository.
- `checkout_multiple_repos.yml` — acquire token and checkout multiple private repositories.

## Run examples

From this repository root:

- `ansible-playbook -i localhost, -c local examples/token_only.yml`
- `ansible-playbook -i localhost, -c local examples/checkout_single_repo.yml`
- `ansible-playbook -i localhost, -c local examples/checkout_multiple_repos.yml`

## Notes

- Replace repository names with real private repositories your app can access.
- The role uses `no_log: true` on sensitive token/key operations.
- Do not print or persist `github_app_auth_token` unless absolutely required.
