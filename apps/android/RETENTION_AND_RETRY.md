# Android Retention, Retry, and Recovery Boundary

The encrypted location-sample queue is intentionally bounded. The current Development contract retains at most 1,000 pending encrypted samples and removes samples older than seven days when retention enforcement runs.

Retention operates only on the app-private encrypted queue. It does not create a plaintext fallback, location-history export, analytics record, or alternate durable store.

Malformed queue entries are quarantined as `.corrupt` files rather than interpreted as valid coordinates. Precise coordinates, bearer credentials, private route history, provider hosts, and sample payloads must not enter ordinary logs or diagnostics.

## Current retry behavior

The Android source now provides a bounded recovery path for already-encrypted pending samples:

- each enqueue establishes a network-constrained retry fallback before the immediate in-process flush;
- `JobScheduler` retries are persisted across reboot and require network availability;
- retry delays use bounded exponential backoff from 30 seconds to 30 minutes;
- the foreground collector, retry job, and manual sync share one process-wide single-flight gate;
- successful sync cancels retry work;
- HTTP 401 clears the protected device credential and stops local collection;
- server `tracking_paused` is classified explicitly and stops local collection rather than being retried or treated as malformed data;
- other non-retryable conflicts remain encrypted for explicit attention rather than being silently discarded; and
- interrupted retry jobs request rescheduling only while a protected credential and encrypted pending work remain.

This retry path never starts location collection itself. It can only flush already-encrypted records under the current protected device credential.

## Remaining acceptance

Still required before production tracking acceptance:

- representative physical-device validation across supported Android versions and vendors;
- process-kill, reboot, connectivity-loss/restoration, and Doze/background-policy validation;
- battery and thermal measurements for the collection profiles;
- permission revocation and credential revocation/re-enrollment recovery testing;
- long-duration queue retention/corruption/recovery testing;
- Privacy Shield, Wardveil Security, Everkeep, Identity, Policy, and Observability acceptance; and
- deployment, rollback, release, and Anchor evidence.

No production tracking or Find My activation is implied by these source primitives.
