# GoreeCloud Location — Backup and Recovery

**Development-preview runbook · 3 November 2026.** All commands are operator-initiated; nothing here starts backup schedules, restores a live production database, or promises professional emergency continuity.

## Recovery scope

GoreeCloud Location stores precise GPS tracks, user accounts, devices, sessions, saved places, events and geofence state in SQLite. Treat every backup as sensitive information. A SQLite snapshot is not encrypted by the application; use authorized storage encryption, restrictive file permissions, secure offline copies and a tested retention policy.

A safe recovery process must verify the data **before** replacing any live service. This software explicitly refuses overwriting existing databases.

## Create a consistent snapshot

Run from a trusted administrative terminal (or the container environment with the same configured database path):

```sh
gclocation backup --destination "$HOME/location-recovery-snapshot.sqlite"
```

The destination directory must exist and the output path must not already exist. The SQLite online backup API captures committed WAL-mode transactions without relying on unsafe file copying. Backup files are created with mode 0600. Do not put a snapshot under a public GitHub repository or shared folder.

## Verify without modification

```sh
gclocation verify-backup --source "$HOME/location-recovery-snapshot.sqlite"
```

The verifier opens the candidate read-only, requires the SQLite file header, checks database integrity and foreign keys, and verifies the expected Location tables. It returns a nonzero exit status if verification fails. A passing check does not prove every feature works on the destination system or that the original data is complete.

## Restore into a NEW database

```sh
gclocation restore --source "$HOME/location-recovery-snapshot.sqlite" \
  --destination "$HOME/location-recovered-new.sqlite"
gclocation verify-backup --source "$HOME/location-recovered-new.sqlite"
```

**Never supply an existing production database as the destination.** The command refuses an existing path, creates a new mode-0600 SQLite file, copies from the verified source, and rechecks the result. It clears copied **user sessions** to prevent old sessions from being replayed after a restore. User passwords and registered device ingestion tokens remain; reissue any credentials believed compromised.

To test a recovery on loopback only, configure `GC_LOCATION_DB` to point to the new file and start a separate trusted instance after choosing a nonconflicting port. Confirm with explicit authentication that expected devices/history are present, exports are correct, and no unauthorized account can read them. Do not connect live tracking clients or switch a production service until you have a reviewed change/rollback plan and appropriate authorization.

## Failure, rollback and retention

- If verification fails, quarantine the candidate, do not switch services, and investigate corruption or schema mismatch.
- Do not overwrite or automatically delete the existing database, its WAL/SHM files, or earlier restore points.
- Protect snapshot copies from unauthorized users. Deleting data from the live database does not erase older backups or downloaded exports.
- Write down the source/target paths and checks performed, but **never** copy passwords, bearer tokens, GPS coordinates or data dumps into public logs/issues.
- Restore and failure tests on synthetic data are required in CI. Production failover, encrypted off-site copies, retention schedules and regular restore drills are future work.

## CLI reference

| Command | Operation |
| --- | --- |
| `gclocation backup --destination NEW_FILE` | WAL-consistent manual snapshot, refuses existing file |
| `gclocation verify-backup --source FILE` | Read-only integrity/schema verification |
| `gclocation restore --source FILE --destination NEW_FILE` | Verified copy to new database, revokes copied login sessions |

See [Architecture](ARCHITECTURE.md), [Security](SECURITY.md) and [Implementation Status](STATUS.md).
