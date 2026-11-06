# Private Circle Membership — Development Foundation

**Status: development preview, November 6, 2026.** GoreeCloud Location supports consent-based circle invitation **metadata only**. **Circle membership does not grant access to GPS positions, devices, history, geofences, exports, alerts, or live maps.** No sharing permissions or emergency overrides exist. Do not describe this as a working family location-sharing service.

## How invitation consent works

1. Accounts are created privately by the self-hosted administrator; there is no public registration or discoverable account directory.
2. A person who wishes to receive a circle invitation signs in to **their own account** and calls `POST /api/circle-invite-code`. The server creates a cryptographically random, one-time code valid for **30 minutes**. Its hash is saved; the plaintext code is returned once.
3. That person deliberately gives the code to a circle owner through a channel they trust. Generating or sharing the code does **not** join a circle or reveal location.
4. A circle owner creates a named circle using `POST /api/circles`, then submits the received code to `POST /api/circles/{id}/invite`. The server consumes the code and creates a pending invitation valid for **7 days**.
5. The invitee sees pending requests through `GET /api/circle-invitations` and responds with an explicit `{"accept":true}` or `{"accept":false}` to `POST /api/circle-invitations/{invitation_id}/respond`.
6. **Only after accepting** does the member see the circle name, owner's username and accepted member roster. Joining is not a GPS sharing grant. Declining means no membership. An account can leave an accepted circle at any time.

## Circles workspace in the browser

Sign in and open **Circles** from the desktop/sidebar or mobile navigation. Create a named circle, or choose **Generate my one-time code** to receive an invite code in a one-time dialog. Share the code **manually and privately** with someone you want to invite you. A circle owner can paste a recipient-supplied code into **Invite by private code**. The intended recipient sees the pending invitation in their own Circles view, and must **Accept** or **Decline**. Joining remains metadata only; the screen always states that GPS sharing is disabled.

Owners can view members and remove pending/accepted members. Accepted members may leave at any time; owners can delete entire circles after confirmation. The UI clears circle lists, invitation codes and member rosters when an account signs out and never accesses another account's GPS data.

The browser implementation is a convenience layer around the owner/recipient authorized API. Server authorization, expiry, caps and revocation remain authoritative. No invitation is sent by email, SMS or push notification. This is not a live family map.

## Authenticated API

| Method | Path | Who can use it | Meaning |
| --- | --- | --- | --- |
| POST | `/api/circles` | Signed-in user | Create named private circle (maximum 20 owned) |
| GET | `/api/circles` | Signed-in user | List owned and explicitly accepted circles only |
| POST | `/api/circle-invite-code` | Signed-in invitee | Replace any older one-time code; return a new 30-minute code |
| POST | `/api/circles/{id}/invite` | Circle owner only | Consume code and create pending 7-day invitation (maximum 20 active invitees) |
| GET | `/api/circle-invitations` | Signed-in invitee | List pending, unexpired invitations addressed to this account |
| POST | `/api/circle-invitations/{id}/respond` | Addressed invitee only | Explicit accept or decline; cannot answer again |
| GET | `/api/circles/{id}/members` | Owner / accepted member | Owner sees active pending + accepted; member sees accepted only |
| DELETE | `/api/circles/{id}/members/{account_id}` | Circle owner | Revoke any pending or accepted member immediately |
| DELETE | `/api/circles/{id}/membership` | Accepted member | Leave the circle without changing GPS records |
| DELETE | `/api/circles/{id}` | Circle owner | Delete the circle and pending/accepted memberships |

All these routes require an **account session**, not an ingestion-only device token. The request and response models reject unsupported fields and invalid Boolean values. Guessed IDs and cross-account requests return 404; invitation expiry is verified at acceptance, not only at listing time. A fresh one-time code can replace an older declined or expired invitation. There is no public invitation link and the server sends no email, push notification, or SMS.

### Example without revealing live GPS

Recipient calls:

```sh
curl -X POST http://127.0.0.1:8123/api/circle-invite-code \
  -H 'Authorization: Bearer RECIPIENT_ACCOUNT_SESSION'
```

The recipient privately gives the one-time `invite_code` to the circle owner. The owner calls:

```sh
curl -X POST http://127.0.0.1:8123/api/circles/1/invite \
  -H 'Authorization: Bearer OWNER_ACCOUNT_SESSION' \
  -H 'Content-Type: application/json' \
  -d '{"invite_code":"PRIVATE_ONE_TIME_CODE"}'
```

No sharing begins. The recipient must independently accept the resulting invitation. These commands are examples for a **private loopback development service**. Never place real tokens in publicly shared shell histories, source code, screenshots or URLs.

## Privacy, security and lifecycle

- Circle names and accepted member usernames are metadata. Do not use them to store sensitive locations or medical/personal safety information.
- Codes are generated from a cryptographic random source and hashed at rest. A code expires after 30 minutes, is invalidated by generating a replacement, and is consumed when an invitation succeeds. A recipient cannot be discovered by searching usernames in this feature.
- Invitations expire after 7 days. Expired or declined requests do not create membership. They can be replaced only with a new code deliberately supplied by the invitee.
- Circle creators are the only owners, with no automatic role promotions or broader administrative powers. Member revocation and leaving take effect on subsequent authenticated API requests.
- Device history, live points, map tiles, export routes, geofence events and private collection controls **remain independently account-scoped**, including after a circle is accepted.
- The schema is additive. Deleting a circle removes its memberships; deleting an account removes circles owned by it and its memberships elsewhere, through SQLite foreign keys. No existing GPS history or device key is migrated.
- Circle membership is a **future sharing prerequisite**, not evidence of a user's consent to be tracked or to share previous data. Separate live/history permission grants, expiry, pause and immediate revocation require their own design and tests before any location-sharing launch.
- This preview has no real multi-device or production test. Do not use it as a family safety service or emergency communications tool.

Related: [API](API.md), [Security](SECURITY.md), [Product spec](PRODUCT_SPEC.md), [Status](STATUS.md).

## Immediate revocation of unused codes

An invitee can choose **Revoke my unused code** in the Circles view and confirm, or call authenticated `DELETE /api/circle-invite-code`. An authorized call returns HTTP 204 even when no code is active. The old code cannot be used to create a new invitation; the user can intentionally generate a new one later. Only the signed-in account's code is affected.

**Revocation does not cancel invitations that were already sent or revoke accepted memberships.** Pending invitations must be declined separately; accepted members can leave; owners may remove members. Codes copied to the operating-system clipboard or external messages cannot be erased by the server. Circle membership still grants **no GPS data or location sharing**.

## Proposed sharing controls — security review required

Circle membership is **not** a live or historical GPS grant. A proposed future sharing phase would require separate source-owner and recipient consent, exact device and member scope, independent history permissions, explicit expiry, and immediate revocation checks. These design gates are documented in [Circle sharing security design](CIRCLE_SHARING_SECURITY_DESIGN.md); they are **not implemented or enabled**. A deployment or PR merge alone cannot authorize exposing another account's coordinates.
