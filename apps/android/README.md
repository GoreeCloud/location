# GoreeCloud Location for Android

The Android client is a native Kotlin application because reliable foreground/background-aware location collection, permissions, battery behavior, protected local buffering, device-scoped authentication, and recovery behavior are central to GoreeCloud Location.

The client remains **Development** software. It must not be presented as production tracking or Find My functionality.

## Current Milestone 2 implementation

The Android client now provides:

- native Android platform APIs without Google Play Services or AndroidX dependencies;
- explicit fine-location and notification permission flows;
- user-visible tracking start/stop controls;
- a foreground location service with persistent Android notification;
- GPS and network provider collection through `LocationManager`;
- explicit one-time device enrollment against `POST /api/v1/devices`;
- user credentials held only in memory for the enrollment request and never persisted by the client;
- device-scoped credential protection using AES-GCM key material generated inside Android Keystore;
- encrypted durable pending-location queue records using a separate Android Keystore AES-GCM key;
- client-generated sample UUIDs preserved across retries for server-side idempotency;
- device-authenticated synchronization to `POST /api/v1/locations`;
- acknowledgement-based queue removal only after HTTP 200/201 success;
- preservation of encrypted pending samples across offline/server failures;
- network-constrained JobScheduler retry persisted across reboot;
- bounded 30-second to 30-minute exponential backoff;
- a process-wide single-flight gate shared by foreground, scheduled, and manual queue flushes;
- explicit server tracking-pause handling that stops local collection;
- explicit handling for conflicts and revoked device authentication;
- HTTPS enforcement for non-local endpoints; and
- local cleartext networking limited to Android emulator/localhost development hosts.

## Storage boundary

Plaintext device credentials are not stored in SharedPreferences or files. The protected credential record is AES-GCM encrypted using an Android Keystore key before being written to private application preferences.

Precise queued location samples are serialized only long enough to encrypt them and are stored as AES-GCM ciphertext under the application's private files directory. Separate Keystore aliases are used for device-authentication material and queued location samples. Corrupt queue records are quarantined rather than silently interpreted or uploaded.

The current in-process latest-observation fields remain diagnostic state only and are cleared when the collector service stops.

## Synchronization boundary

Each location observation receives a UUID `client_sample_id` before it is encrypted locally. The same identifier and payload are reused until the server acknowledges the sample, matching the native API's idempotency contract.

Synchronization:

1. persists a network-constrained retry fallback for queued work before the immediate flush;
2. loads the protected device credential;
3. decrypts queued samples only inside the application process as needed for upload;
4. serializes foreground, scheduled, and manual flushes through one process-wide single-flight gate;
5. sends samples to `/api/v1/locations` using the device bearer credential;
6. removes a queue record only after a successful 200/201 response;
7. leaves records encrypted when the network is unavailable or the server rejects a transient operation;
8. uses bounded persisted exponential backoff for retryable failure;
9. clears a revoked/unauthorized device credential after HTTP 401 so tracking cannot continue under invalid authority; and
10. stops local collection when the server reports `tracking_paused`, preserving server privacy authority.

## Privacy and safety boundary

The Android client does not implement covert tracking, hide required operating-system indicators, bypass Android permission controls, silently enroll a device, write precise coordinates to ordinary logs, or fall back to plaintext buffering.

The current enrollment screen is a development bridge until GoreeCloud Identity provides the final device-authorization flow. Production approval still requires broader Android lifecycle, process recovery, battery, retention, Privacy Shield, Wardveil Security, Everkeep, and representative-device acceptance.

## Next work

Remaining Milestone 2 Android work is now concentrated in representative physical-device validation, process-kill/reboot/Doze and connectivity-restoration testing, long-duration battery/thermal evidence, permission and re-enrollment recovery, expanded encrypted-queue recovery testing, device enrollment through GoreeCloud Identity, and production platform-system acceptance.
