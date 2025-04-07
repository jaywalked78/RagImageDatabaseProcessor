[![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-dark.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-light.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)DOCS](https://supabase.com/docs)

-   [Start](https://supabase.com/docs/guides/getting-started)
-   Products
-   Build
-   Manage
-   Reference
-   Resources

[![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-dark.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-light.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)DOCS](https://supabase.com/docs)

Search docs...

K

Realtime

1.  [Realtime](https://supabase.com/docs/guides/realtime)

3.  Usage

5.  [Presence](https://supabase.com/docs/guides/realtime/presence)

# 

Presence

## 

Share state between users with Realtime Presence.

* * *

Let's explore how to implement Realtime Presence to track state between multiple users.

## Usage[#](#usage)

You can use the Supabase client libraries to track Presence state between users.

### Initialize the client[#](#initialize-the-client)

Go to your Supabase project's [API Settings](https://supabase.com/dashboard/project/_/settings/api) and grab the `URL` and `anon` public API key.

JavaScriptDartSwiftKotlinPython

```
123456import { createClient } from '@supabase/supabase-js'const SUPABASE_URL = 'https://<project>.supabase.co'const SUPABASE_KEY = '<your-anon-key>'const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
```

### Sync and track state[#](#sync-and-track-state)

JavaScriptDartSwiftKotlinPython

Listen to the `sync`, `join`, and `leave` events triggered whenever any client joins or leaves the channel or changes their slice of state:

```
1234567891011121314const roomOne = supabase.channel('room_01')roomOne  .on('presence', { event: 'sync' }, () => {    const newState = roomOne.presenceState()    console.log('sync', newState)  })  .on('presence', { event: 'join' }, ({ key, newPresences }) => {    console.log('join', key, newPresences)  })  .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {    console.log('leave', key, leftPresences)  })  .subscribe()
```

### Sending state[#](#sending-state)

You can send state to all subscribers using `track()`:

JavaScriptDartSwiftKotlinPython

```
12345678910111213const roomOne = supabase.channel('room_01')const userStatus = {  user: 'user-1',  online_at: new Date().toISOString(),}roomOne.subscribe(async (status) => {  if (status !== 'SUBSCRIBED') { return }  const presenceTrackStatus = await roomOne.track(userStatus)  console.log(presenceTrackStatus)})
```

A client will receive state from any other client that is subscribed to the same topic (in this case `room_01`). It will also automatically trigger its own `sync` and `join` event handlers.

### Stop tracking[#](#stop-tracking)

You can stop tracking presence using the `untrack()` method. This will trigger the `sync` and `leave` event handlers.

JavaScriptDartSwiftKotlinPython

```
123456const untrackPresence = async () => {  const presenceUntrackStatus = await roomOne.untrack()  console.log(presenceUntrackStatus)}untrackPresence()
```

## Presence options[#](#presence-options)

You can pass configuration options while initializing the Supabase Client.

### Presence key[#](#presence-key)

By default, Presence will generate a unique `UUIDv1` key on the server to track a client channel's state. If you prefer, you can provide a custom key when creating the channel. This key should be unique among clients.

JavaScriptDartSwiftKotlinPython

```
123456789import { createClient } from '@supabase/supabase-js'const channelC = supabase.channel('test', {  config: {    presence: {      key: 'userId-123',    },  },})
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/realtime/presence.mdx)

### Is this helpful?

No Yes

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)