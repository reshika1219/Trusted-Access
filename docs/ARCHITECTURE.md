# Architecture baseline

The system should remain modular around these boundaries:

- Authentication and secure sessions
- User profiles
- Vault categories and encrypted records
- Encrypted file metadata and storage
- Key management and recovery
- Trusted contacts
- Access policies
- Emergency requests and approvals
- Temporary access grants
- Audit events
- Development notifications

The data model must support users, trusted contacts, categories, vault items,
access policies, emergency requests, approvals, access grants, audit events, and
encrypted file metadata. Authorization must be enforced at the service
boundary, not only in the user interface.

The initial implementation should keep the storage and application boundaries
replaceable so that a local prototype can later be evaluated against a
zero-knowledge or client-side-encryption deployment model.

## Current modules

- `main.py`: app, owner authentication, throttling, security-header middleware
- `vault.py`: encrypted vault items and the audit helper
- `contacts.py`: trusted contacts, invites, sharing policies
- `requests.py`: contact-authenticated access requests
- `access.py`: approvals, grants, revocation, audit listing
- `portal.py`: read-only views for a signed-in trusted contact
- `keys.py`: contact public keys, owner fingerprint confirmation, and the
  encrypted shares and wrapped keys that implement key delivery
- `backup.py`: export contract and import audit notice
- `ui.py`: the single-page dashboard and its Content-Security-Policy
- `database.py`: SQLite schema and migrations (foreign-key cascades end access
  on deletes)

Owner and contact credentials are separate (`X-Session-Token` and
`X-Contact-Token`), so a contact token can never act as an owner session.
