# Proposal: a public, read-only check-in feed for Ham.Live

**For:** the operator of the `skywarn.na0d.com` Ham.Live instance (NA0D)
**Status:** proposal for review. Nothing here has been applied to any Ham.Live copy, and none of it has been run against a live instance.

## Why

The Skywarn Net Check-in Map shows where stations are as they check in to a net. It needs to know, while a net is running, which stations have checked in and the town each one entered.

Today that data is behind a login:

| Endpoint | Auth | Useful for the map? |
| --- | --- | --- |
| `GET /api/data/livenets` | none (public) | Yes, for finding the running net by ID |
| `GET /api/data/livenets/:id` | `REQ_CALLSIGN` | Has the stations, but needs a signed-in account |
| `GET /api/sse/livenets/:id` | session cookie | Same |

The map has no account, and sign-in is by emailed magic link, which is a poor fit for an unattended service. Rather than store a login for the map, the simplest fix is one small public endpoint that returns only what the map needs.

## Proposed endpoint

`GET /api/data/livenets/:id/checkins`

- Public, read-only, no cookies.
- **Opt-in per net.** It answers only for net IDs listed in a new setting, `PUBLIC_CHECKIN_NET_IDS` (comma-separated). Any other net gets a 404. Stations who check in to other nets never become visible.
- **Allow-list of fields.** Each entry has exactly three fields: `callSign`, `location`, `checkedInAt`. The station record also holds `email`, `displayName`, `photo`, `userProfile`, signal reports, and presence data. None of those are returned, and the code builds the response by picking fields, not by copying the document.
- Only stations with `checkedState === true` are returned. Spectators and checked-out stations are left out.
- Cached for 3 seconds per net, the same as the existing public net list, so many map viewers cost one database read per 3 seconds.
- Does not record presence, so polling it never makes anyone look like a participant.

Example response:

```json
{
  "endpointVersion": "1.0",
  "now": 1763769600000,
  "servedFromCache": false,
  "started": true,
  "closing": false,
  "checkins": [
    { "callSign": "N5XFW", "location": "Royal, AR", "checkedInAt": "2026-11-18T01:11:43.285Z" }
  ]
}
```

The map finds the right net with the existing public `GET /api/data/livenets` (it matches on title and `started: true`), then polls the new endpoint every few seconds.

## Proposed code

Written against the code as it appears in `server/dist/` of the open-source edition. File names and line positions may differ in the deployed instance, so treat these as snippets.

### 1. `server/dist/routes/dataLiveNetRoutes.js`

```js
const { liveNetList, liveNetCreatePost, liveNetDetails, liveNetCheckins } = require('../controllers/liveNetController');

router.get('/', liveNetList);
router.get('/:id/checkins', liveNetCheckins);   // public, read-only, opt-in per net
router.post('/:id', authCheck(REQ_CALLSIGN), liveNetCreatePost);
router.get('/:id', authCheck(REQ_CALLSIGN), liveNetDetails);
```

### 2. `server/dist/controllers/liveNetController.js`

Add near the other caches at the top:

```js
const checkinsCache = new NodeCache({ stdTTL: 3, checkperiod: 60 });
const PUBLIC_CHECKIN_NET_IDS = (process.env.PUBLIC_CHECKIN_NET_IDS || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
```

Add the handler:

```js
// Public, read-only feed of who has checked in to a running net.
// Opt-in per net (PUBLIC_CHECKIN_NET_IDS) and limited to callSign, location, checkedInAt.
const liveNetCheckins = async (req, res) => {
    const { id: npid } = req.params;
    res.set('Access-Control-Allow-Origin', '*'); // read-only, no credentials

    if (!PUBLIC_CHECKIN_NET_IDS.includes(npid)) {
        return res.status(404).json({ endpointVersion: '1.0', errorMessage: 'not found' });
    }

    try {
        const cached = checkinsCache.get(npid);
        if (cached) {
            return res.status(200).json({ ...cached, now: Date.now(), servedFromCache: true });
        }

        const { liveNetDoc } = await helpers.fetchNetProfileAndLiveNet(npid); // throws NetNotFoundError

        const ids = Array.from(liveNetDoc.lookupTable.values()).map(v => v.stationInteraction);
        const docs = await StationInteraction.find({ _id: { $in: ids }, checkedState: true })
            .select('callSign location checkedInAt -_id')
            .sort({ checkedInAt: 1 })
            .lean();

        const body = {
            endpointVersion: '1.0',
            started: liveNetDoc.started,
            closing: liveNetDoc.closing,
            checkins: docs.map(({ callSign, location, checkedInAt }) => ({ callSign, location, checkedInAt }))
        };
        checkinsCache.set(npid, body);
        return res.status(200).json({ ...body, now: Date.now(), servedFromCache: false });
    } catch (err) {
        if (err instanceof NetNotFoundError) {
            return res.status(404).json({ endpointVersion: '1.0', errorMessage: 'not found' });
        }
        logger.error(err.stack);
        return res.status(500).json({ endpointVersion: '1.0', errorMessage: 'internal error' });
    }
};
```

Export it:

```js
module.exports = {
    liveNetList,
    liveNetCreatePost,
    liveNetDetails,
    liveNetPresence,
    liveNetCheckins
};
```

### 3. Configuration

Add to `.env` (and `.env.example`):

```
# Net profile IDs whose check-ins may be read without a login (comma-separated).
# Leave empty to keep the public check-in feed switched off.
PUBLIC_CHECKIN_NET_IDS=
```

Also add a short entry for the endpoint to `docs/api-reference.md`.

## Things to decide or confirm

1. **Consent.** This makes callsign and town visible to anyone who can reach the URL. The check-in details API is login-only today (I did not check whether the net page itself is public), so this may be a change in who can see them. I'd suggest announcing on the net that check-ins appear on a public map, and keeping the town-level detail only. Both sides of that are a decision for the net operators.
2. **Which net ID** to put in `PUBLIC_CHECKIN_NET_IDS`. Is the Skywarn net a permanent net profile with a stable ID, or does each session get a new one? The sample report's Net ID (`6a272aad98dc5195341d3154`) looks like a database ID, so I would expect a permanent profile to keep one ID across sessions, but that needs confirming on the live instance.
3. **After a net closes.** The handler keeps answering while the live net document exists, with `closing: true`. Please check what happens to station records once the net is closed and cleaned up, because the map should stop polling then.
4. **CORS.** The `*` header lets a map hosted anywhere read the feed. If the map will be hosted at one known address, replace `*` with that origin.
5. **Source vs. build.** The repo has controllers only under `server/dist/`, with `server/src/` holding shared code. Make the change in whichever files are authoritative on the deployed instance.
6. **Rate limiting.** The 3-second cache bounds database load, but a public endpoint may deserve the same rate limiting as other public routes, if the instance has any.

## Suggested checks before going live

- With `PUBLIC_CHECKIN_NET_IDS` empty, the endpoint returns 404 for every net.
- With the Skywarn net ID set, it returns only the three fields, and the response contains no `email`, `displayName`, `photo`, or `userProfile`.
- A station that checks out disappears from the list; a spectator never appears.
- A second net's ID, not in the list, returns 404.
- Calling it repeatedly does not change anyone's presence in the net.
