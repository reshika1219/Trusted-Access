# Trusted Access

Trusted Access is a privacy-first prototype for controlled emergency
information sharing. A person prepares encrypted critical information in
advance and grants selected, auditable access to trusted people only through
explicit approval workflows.

> **Prototype warning:** This project is not production-secure, legally
> certified, a substitute for a will or power of attorney, or a guarantee that
> emergency access will work in every situation. It has not had a professional
> security review. Do not store real secrets in it.

## What it does

**For the owner** (browser dashboard at `/`):

- Create an account, or try a one-click **demo account** with sample data.
- Store text items (medical, insurance, documents, pets, instructions, ...)
  encrypted in the browser before they are sent. Edit or delete them.
- Add trusted contacts, who get **no access** until you choose what they may
  request. Create an invite token or link for each contact.
- Set **sharing rules** per item: which contacts may request it and how many
  approvals are needed. Rules are replaced on save, and narrowing them ends
  access immediately. **Stop sharing** makes an item private again.
- Approve or reject access requests. Approving creates a read-only grant that
  expires after one hour. **Revoke** a grant at any time.
- Review an owner-visible **activity log** of every security-relevant event.
- Download a **backup encrypted in the browser** with a passphrase you choose,
  and restore from one (validated, additive, duplicate-safe).

**For a trusted contact** (the "I'm a trusted contact" link, or an invite link):

- Your browser creates an encryption key the first time you sign in. You read
  its fingerprint to the owner, who confirms it.
- See only the items an owner shared with you (never ciphertext in listings).
- Request access, approve other contacts' requests when you are an approver
  (you can never approve your own), and open an item while your grant is active.
  It decrypts in your browser with a key the owner delivered in advance, so it
  works even when the owner is offline.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest
uvicorn trusted_access.main:app --reload
```

Open <http://127.0.0.1:8000/> and click **Try the demo**. Interactive API
documentation is at `/docs`, and `/health` reports service status. Data is kept
in `.data/trusted_access.sqlite3` (override with `TRUSTED_ACCESS_DB`).

To see the contact side, open **Contacts -> Create invite -> Open contact view**
in the demo. It opens a second tab as that contact.

## How a request flows

1. A contact signs in with their invite. Their browser creates a keypair and
   registers the public key. They read the fingerprint to the owner.
2. The owner compares fingerprints and confirms the key.
3. The owner shares an item with contacts (a policy: contacts + approvals). The
   owner's browser delivers a copy of the item that only the confirmed contacts'
   keys can open.
4. A contact asks for the item. Nothing is released yet.
5. The owner approves (or, for multi-approval items, other contacts approve).
   A read-only grant is created that expires after one hour.
6. While the grant is active the server hands the contact the encrypted copy
   and their wrapped key. The contact decrypts it in their browser.
7. Every step is written to the owner's audit log. The owner can revoke the
   grant, stop sharing, or delete the item at any time.

## Key delivery

The server never sees a decryption key:

- Each contact's browser generates an RSA-OAEP (3072-bit) keypair. The private
  key is non-extractable and stays in the browser (IndexedDB).
- The owner confirms the contact's key by fingerprint, out of band. A key that
  changes later loses confirmation and any keys wrapped to it.
- When sharing, the owner's browser encrypts a copy of the item under a fresh
  random AES-256-GCM key and wraps that key to each confirmed contact with
  RSA-OAEP. Every publish uses a new key.
- The server stores the encrypted copy and the wrapped keys and releases them
  only while a grant is active. Editing an item or changing its sharing rules
  clears the old copy, and the owner's browser publishes a fresh one.

## API overview

| Area | Endpoints |
| --- | --- |
| Owner auth | `POST /auth/register`, `/auth/login`, `/auth/logout`, `GET /auth/me` |
| Vault | `POST/GET /vault/items`, `GET/PUT/DELETE /vault/items/{id}` |
| Sharing | `GET/PUT/DELETE /vault/items/{id}/policy` |
| Contacts | `POST/GET /trusted-contacts`, `DELETE /trusted-contacts/{id}`, `POST .../invite` |
| Requests | `POST /access-requests` (contact), `GET /access-requests` (owner), `.../approve`, `.../reject`, `.../contact-approve` |
| Grants | `GET /access-grants`, `GET /access-grants/{id}` (contact), `POST .../revoke` |
| Key delivery | `PUT /contact/key`, `POST /trusted-contacts/{id}/key/confirm`, `PUT /vault/items/{id}/share`, `GET /vault/policies` |
| Contact portal | `GET /contact/me`, `/contact/items`, `/contact/requests`, `POST /contact/logout` |
| Audit / backup | `GET /audit-events`, `GET /backup/export`, `POST /backup/import` |

Owners authenticate with `X-Session-Token`, contacts with `X-Contact-Token`.
Every read and write is authorised on the server, not only in the UI.

## Security summary

- Vault text is encrypted in the browser (AES-GCM). The server stores
  ciphertext only and never logs plaintext.
- Backups are fully encrypted in the browser (PBKDF2-SHA256 + AES-256-GCM) with
  a passphrase the server never sees.
- Passwords use Argon2. Sessions and contact tokens are stored hashed. Sign-out
  ends the session on the server. Failed logins are throttled per email.
- The page is served with a hash-based Content-Security-Policy (one allowed
  inline script, no outside connections), plus `nosniff`, no-referrer,
  frame-ancestors none, a permissions policy that disables camera, microphone
  and location, and `no-store` caching.
- All user content is HTML-escaped before rendering, and imported files are
  treated as untrusted input.

See the [threat model](docs/THREAT_MODEL.md) for scope and known limits.

## Known limitations

These are deliberate prototype boundaries, not oversights:

- **Contact keys live in one browser.** A contact who loses it (or switches
  browser) must create a new key, and the owner must confirm it again. Items are
  delivered to contacts only after the owner has confirmed their key, so a
  contact who never set one up cannot read anything.
- **Fingerprint checking is manual.** If an owner confirms without comparing, a
  malicious server could substitute a key. This is the usual trade-off of
  end-to-end encryption without a trusted directory.
- **Something a contact already opened can't be taken back.** Revoking stops
  future access and rotates keys, but cannot erase what they saw.
- **No recovery key for the owner.** The owner's vault key lives in their
  browser (`localStorage`). Lose it and the owner's own encrypted items are
  gone. Shared copies already delivered to contacts remain readable by them.
- The server database is not encrypted at rest, and titles, categories and
  contact details are stored in plaintext on the server.
- Policy `access_mode` (specific contacts / emergency only / time limited) is
  recorded but does not change behaviour yet. Grants always last one hour. There
  are no waiting periods, automatic release, notifications, or attachments.
- No email verification, password reset, or two-factor authentication.
- Login throttling is in-memory and per process.

## Documentation

- [Project plan](docs/PROJECT_PLAN.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Architecture](docs/ARCHITECTURE.md)

## Development

`python -m pytest` runs the test suite (it also syntax-checks the dashboard's
embedded JavaScript when Node.js is installed). It supports Python 3.9 and
newer. Contributions should follow `.github/copilot-instructions.md`: small
vertical slices, tests for authorization, expiry, approvals, and audit events.
