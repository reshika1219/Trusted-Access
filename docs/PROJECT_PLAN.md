# Project plan

## Current state

The repository started empty: there were no source files, commits, branches,
framework configuration, database schema, tests, or existing functionality.
This first change establishes the project contract and research baseline.

## Minimal implementation order

1. Confirm the application stack, deployment boundary, key-management model,
   and development authentication approach.
2. Define the initial schema and encrypted vault-record format.
3. Implement local authentication and encrypted text records.
4. Add trusted contacts and per-item permission checks.
5. Add owner-approved, temporary, read-only access grants.
6. Add multi-party approval rules, waiting periods, revocation, and audit
   views.
7. Add encrypted export/import and carefully validated file attachments.
8. Add development notifications, recovery UX, threat-model review, and
   security testing.

The current implementation has reached the recovery/export contract. The
server deliberately does not decrypt imported backup payloads or promise key
recovery; client-side decryption and validation remain required. The dashboard
now encrypts the entire backup file in the browser with a user-chosen
passphrase (see the backup section of the threat model) and validates files
before restoring them.

## First vertical slice

The first slice should demonstrate this complete path:

1. An owner creates an account and a vault item.
2. The item is encrypted before persistence.
3. The owner adds a trusted contact without granting access.
4. The contact requests one permitted item.
5. The owner explicitly approves the request.
6. The system creates a read-only grant with an expiry.
7. The recipient views only that item.
8. The owner can see the request, approval, grant, view, and expiry events.

## Confirmed decisions

- Python with FastAPI and SQLite
- Client-side encryption; the server stores ciphertext only
- File attachments are deferred until text records and permissions work

## Decisions requiring confirmation

- Backend language and web framework
- Database and deployment model
- Whether encryption is performed entirely client-side or by a local trusted
  application boundary for the prototype
- Recovery-key and encrypted-export UX
- Notification mechanism for development
- Whether file attachments are deferred until text records are validated

These decisions materially affect the threat model and should not be hidden
behind an arbitrary default.
