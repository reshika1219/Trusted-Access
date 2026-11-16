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

The stack is intentionally not selected yet. It is a security-critical decision
that should be confirmed before implementation.

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

Setup and test commands will be documented after the language, framework, and
database are selected.
