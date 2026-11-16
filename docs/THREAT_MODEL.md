# Threat model

## Assets

- Vault text and future file contents
- Recovery keys and encryption key material
- Trusted-contact identities and relationship data
- Access policies, requests, approvals, and active grants
- Audit history

## Threats in scope

- Stolen authenticated session
- Malicious or over-curious trusted contact
- Curious or compromised server administrator
- IDOR and broken object-level authorization
- Replayed or modified approval requests
- Unauthorized audit-record modification
- Leaked logs or backups
- Malicious file uploads
- Accidental owner over-sharing

## Security goals

- Vault plaintext is not persisted on the server.
- Every access is checked against the owner-defined policy.
- Access is limited to explicitly approved records or categories.
- Grants are read-only by default and expire.
- Approval and access events are visible to the owner.
- Secrets are absent from logs and error messages.

## Explicit non-goals for the initial prototype

- Protection from a fully compromised user device
- Protection when a user voluntarily reveals a password or recovery key
- Guaranteed availability during every emergency
- Protection from all legal compulsion, which depends on deployment
- Recovery after all recovery keys are lost
- Complete metadata privacy where the selected architecture cannot provide it
- Legal validity of an emergency request or inheritance instruction

## Safety boundaries

The product must not continuously track devices, monitor users, read private
messages, or use AI to observe a person's life. Automatic release must never be
presented as legally valid or enabled without explicit configuration, warnings,
waiting-period semantics, and audit events.
