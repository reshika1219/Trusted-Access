# Trusted Access

Trusted Access is a privacy-first prototype for controlled emergency
information sharing. A person prepares encrypted critical information in
advance and grants selected, auditable access to trusted people only through
explicit emergency workflows.

> **Prototype warning:** This project is not production-secure, legally
> certified, a substitute for a will or power of attorney, or a guarantee that
> emergency access will work in every situation.

## Current status

The repository is at project initialization. The first implementation milestone
is a small vertical slice with local development authentication, encrypted text
vault records, trusted contacts, per-item permissions, owner-approved temporary
read-only access, and owner-visible audit events.

The initial stack is Python, FastAPI, and SQLite. Vault encryption is intended
to happen client-side; the server must persist ciphertext rather than plaintext.
File attachments are deferred until text records and permissions are validated.

## Principles

- Privacy by default and user-controlled encryption
- Least-privilege, explicit consent, and revocable access where possible
- No continuous tracking or always-on sensors
- No plaintext sensitive vault content on the server
- Visible prototype limitations and auditable security events

## Documentation

- [Project plan](docs/PROJECT_PLAN.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Architecture](docs/ARCHITECTURE.md)

## Development

Create a virtual environment and install the project with test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
pytest
uvicorn trusted_access.main:app --reload
```

Open `http://127.0.0.1:8000/` for the browser dashboard. The interactive API
documentation remains available at `http://127.0.0.1:8000/docs`, and the health
endpoint is available at `http://127.0.0.1:8000/health`.

The browser dashboard is a prototype interface. It encrypts vault text in the
browser before submission, but its demonstration key is kept in browser
storage; do not use real-life secrets until the key-management and recovery
design has received a professional security review.
