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

## Backups

The dashboard downloads an encrypted backup (format version 2). The whole
payload, including titles, categories, and trusted contacts, is encrypted in
the browser with AES-256-GCM using a key derived from a user-chosen passphrase
(PBKDF2-SHA256, 600,000 iterations, random salt and IV per export). The file
header is bound as authenticated data. The server never receives the
passphrase or the plaintext backup, and import only sends it the ciphertext for
the audit trail.

Known limits:

- The server still stores titles, categories, and contacts as plaintext and
  returns them to the owner at export time. Only the downloaded file is fully
  encrypted.
- Passphrase strength is the user's responsibility; only a 12-character minimum
  is enforced. PBKDF2 is not memory-hard (the Web Crypto API has no Argon2).
- Lost passphrases cannot be recovered by the server.
- Backups do not contain the browser-held vault encryption key or sharing
  policies. Restored items are private and decrypt only in a browser that holds
  the original key.
- Older unencrypted (version 1) backups can still be imported, with a warning.
- Imported files are untrusted: headers, KDF cost, record shapes, sizes, and
  counts are validated, and restored records are created through the normal
  authorised APIs.

## Authorization and web hardening

- Every endpoint authorises on the server. Owner resources are filtered by
  owner, contact resources by the contact's policy membership. Other users'
  resource IDs return 404.
- A requester cannot approve their own access request, and a contact cannot hold
  two open requests for the same item.
- Saving a sharing policy replaces the old one. Narrowing or removing it rejects
  open requests and revokes active grants of contacts no longer included.
- Sign-out deletes the session on the server. Failed logins are throttled per
  email (10 failures per 15 minutes). The throttle is in-memory, per process,
  and lets someone lock out a known email for the window. A real deployment
  needs a shared rate limiter.
- The page is served with a Content-Security-Policy that allows only its own
  inline script by hash, blocks inline event handlers and outside connections,
  and forbids framing. A permissions policy disables camera, microphone and
  geolocation. Responses are `no-store`. User content is escaped before it is
  rendered.
- Invite links carry the contact token in the URL fragment, which browsers do
  not send to the server. The page removes it from the address bar on load.

## Key delivery

Contacts read shared items through end-to-end encryption, not through the
server:

- Each contact's browser generates an RSA-OAEP (3072-bit, SHA-256) keypair with a
  non-extractable private key kept in IndexedDB. Only the public key is sent.
- The owner confirms the key by comparing its SHA-256 fingerprint out of band,
  and the server verifies that the key being confirmed is the one it holds. A
  replaced key loses confirmation, and wrapped keys for the old key are
  deleted. Publishing to an unconfirmed key is refused.
- For each share, the owner's browser encrypts the item under a fresh random
  AES-256-GCM key and wraps it to each confirmed contact with RSA-OAEP. The
  server stores only ciphertext and wrapped keys and releases them to a contact
  only while one of their grants is active.
- Editing an item, changing its rules, or stopping sharing deletes the stored
  copy so stale content or keys are never served.

What this does not protect against:

- An owner who confirms a fingerprint without comparing it. A malicious server
  could then substitute its own key and decrypt what is delivered. Compare
  fingerprints over a channel the server does not control.
- A stolen invite token. An attacker can register their own key, but delivery
  needs the owner's confirmation, which will not match the real contact.
- A contact who already opened an item. Revocation and key rotation cannot
  erase what they saw or copied.
- A compromised contact browser, which holds the contact's private key.
- Loss of a contact's browser key. The contact creates a new one and the owner
  re-confirms.

## Known gaps

- No owner recovery key (the vault key lives in the owner's browser), and no
  email verification, password reset, or two-factor sign-in.
- Server-side metadata (titles, categories, contact details, the access graph)
  is not hidden from the server.
- Policy access modes are recorded but not yet enforced differently, and grants
  always last one hour.
- The SQLite database is not encrypted at rest.
