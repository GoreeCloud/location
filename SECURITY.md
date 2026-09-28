# GoreeCloud Location — Security

## Security status

GoreeCloud Location is Forge/Development. Security-sensitive features remain acceptance-gated.

## Reporting vulnerabilities

Use GitHub private vulnerability reporting or another approved private GoreeCloud maintainer channel when available. Do not post reusable credentials, private user location data, or sensitive operational details in public issues.

## Authentication and authorization

- User and device credentials are distinct.
- Ownership is derived from authenticated identity/device state, never request-supplied user identifiers.
- Device revocation and tracking pause are server-enforced.
- Every user-owned API/resource path requires explicit authorization.
- Administrative service authority must not imply unrestricted user-location access.

## Sensitive-data handling

Reusable credentials, tokens, signing material, recovery secrets, and private keys must not be committed to the repository or written into ordinary logs. Raw precise coordinates must be excluded from routine logs and diagnostics.

## Find My and anti-abuse

Recovery, nearby/offline finding, destructive actions, and network-style discovery require dedicated abuse-prevention, anti-stalking, privacy, cryptographic, recovery, Policy, Observability, and Wardveil acceptance before activation.

## Android and device security

Native collection must respect Android permission/background-execution rules, preserve credential revocation, use bounded/offline storage safely, and recover without silently resuming behavior that the user or server disabled.

## Production gate

Security review, production Identity, provider/network acceptance, anti-abuse evidence, continuity/restore, representative-device validation, deployment, rollback, and release qualification remain separate gates before Anchor.
