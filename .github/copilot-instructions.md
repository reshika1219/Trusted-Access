# Trusted Access Project Guidelines

## Mission

Trusted Access is a privacy-first prototype for controlled emergency information
sharing. It is not a password manager, surveillance tool, substitute for legal
estate planning, or legally certified emergency-release system.

## Security and privacy

- Never store or log plaintext vault content, passwords, tokens, recovery keys,
  or encryption keys.
- Use established cryptographic libraries and authenticated encryption; never
  invent cryptography.
- Enforce least privilege on the server for every read and write.
- Treat all uploaded files, filenames, identifiers, and client input as
  untrusted.
- Make prototype-only emergency behavior explicit in the UI and documentation.
- Record security-relevant actions in an owner-visible, tamper-evident audit
  design.
- Do not add device tracking, background monitoring, microphone/camera access,
  private-message access, or hidden data collection.

## Development workflow

- Prefer one small, complete vertical slice over broad unfinished features.
- Add or update tests for authorization, permission boundaries, expiry,
  approval rules, recovery, and audit events when those areas change.
- Run the smallest relevant formatter, type checker, and test command before
  committing.
- Do not claim production security until a professional security review has
  occurred.
- Make one coherent change at a time and create a Git commit immediately after
  validating it. Use a descriptive commit message and include the required
  Copilot co-author trailer.
- Never amend or rewrite commits unless the user explicitly asks.

## Documentation

Keep the threat model, security assumptions, prototype limitations, and setup
instructions current with implementation changes. Use clear language suitable
for non-technical families.
