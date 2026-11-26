# Project plan

## Current state

The first vertical slice and most of the original plan are implemented and
tested (see the README for features). Status against the minimal order:

1. Stack and boundaries: done (Python, FastAPI, SQLite, client-side encryption).
2. Schema and encrypted record format: done (`v1:<iv>:<ciphertext>`, AES-GCM).
3. Local authentication and encrypted text records: done, including edit and
   delete, server-side logout, and failed-login throttling.
4. Trusted contacts and per-item permission checks: done. Policies are replaced
   on save and narrowing them revokes access immediately.
5. Owner-approved, temporary, read-only grants: done (fixed one-hour expiry).
6. Multi-party approvals, revocation, audit views: done. Requesters cannot
   approve their own requests. Waiting periods are **not** implemented.
7. Encrypted export/import: done (whole-payload passphrase encryption). File
   attachments remain deferred.
8. Notifications, recovery UX, threat-model review, security testing:
   partially done. There are no notifications and no recovery key. The threat
   model is current but has not had a professional review.

A browser dashboard covers the owner and trusted-contact workflows. Key
delivery to contacts is implemented (RSA-OAEP wrapped per-share keys with owner
fingerprint confirmation), so contacts can decrypt shared items in their own
browser while the owner is offline.

## Next steps

1. Add an owner recovery key and a recovery flow for the browser vault key.
2. Strengthen contact key setup: a second device per contact, and an easier
   way to compare fingerprints (for example a short code read aloud).
3. Make `access_mode` real: waiting periods, time-limited windows, and
   configurable grant lifetime.
4. Development notifications (for example, email to a local sink).
5. Validated file attachments.
6. A professional security review before any claim of production security.

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

## Decisions still requiring confirmation

- Recovery-key UX
- Notification mechanism for development
- Deployment model beyond a local prototype

These decisions materially affect the threat model and should not be hidden
behind an arbitrary default.
