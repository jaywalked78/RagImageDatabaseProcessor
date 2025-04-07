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

3.  Deep dive

5.  [Architecture](https://supabase.com/docs/guides/realtime/architecture)

# 

Realtime Architecture

* * *

Realtime is a globally distributed Elixir cluster. Clients can connect to any node in the cluster via WebSockets and send messages to any other client connected to the cluster.

Realtime is written in [Elixir](https://elixir-lang.org/), which compiles to [Erlang](https://www.erlang.org/), and utilizes many tools the [Phoenix Framework](https://www.phoenixframework.org/) provides out of the box.

![Global Architecture](https://supabase.com/docs/img/guides/realtime/realtime-arch.png)

## Elixir & Phoenix[#](#elixir--phoenix)

Phoenix is fast and able to handle millions of concurrent connections.

Phoenix can handle many concurrent connections because Elixir provides lightweight processes (not OS processes) to work with.

Client-facing WebSocket servers need to handle many concurrent connections. Elixir & Phoenix let the Supabase Realtime cluster do this easily.

## Channels[#](#channels)

Channels are implemented using [Phoenix Channels](https://hexdocs.pm/phoenix/channels.html) which uses [Phoenix.PubSub](https://hexdocs.pm/phoenix_pubsub/Phoenix.PubSub.html) with the default `Phoenix.PubSub.PG2` adapter.

The PG2 adapter utilizes Erlang [process groups](https://www.erlang.org/docs/18/man/pg2.html) to implement the PubSub model where a publisher can send messages to many subscribers.

## Global cluster[#](#global-cluster)

Presence is an in-memory key-value store backed by a CRDT. When a user is connected to the cluster the state of that user is sent to all connected Realtime nodes.

Broadcast lets you send a message from any connected client to a Channel. Any other client connected to that same Channel will receive that message.

This works globally. A client connected to a Realtime node in the United States can send a message to another client connected to a node in Singapore. Connect two clients to the same Realtime Channel and they'll all receive the same messages.

Broadcast is useful for getting messages to users in the same location very quickly. If a group of clients are connected to a node in Singapore, the message only needs to go to that Realtime node in Singapore and back down. If users are close to a Realtime node they'll get Broadcast messages in the time it takes to ping the cluster.

Thanks to the Realtime cluster, you (an amazing Supabase user) don't have to think about which regions your clients are connected to.

If you're using Broadcast, Presence, or streaming database changes, messages will always get to your users via the shortest path possible.

## Connecting to a database[#](#connecting-to-a-database)

Realtime allows you to listen to changes from your Postgres database. When a new client connects to Realtime and initializes the `postgres_changes` Realtime Extension the cluster will connect to your Postgres database and start streaming changes from a replication slot.

Realtime knows the region your database is in, and connects to it from the closest region possible.

Every Realtime region has at least two nodes so if one node goes offline the other node should reconnect and start streaming changes again.

## Broadcast from Postgres[#](#broadcast-from-postgres)

Realtime Broadcast sends messages when changes happen in your database. Behind the scenes, Realtime creates a publication on the `realtime.messages` table. It then reads the Write-Ahead Log (WAL) file for this table, and sends a message whenever an insert happens. Messages are sent as JSON packages over WebSockets.

The `realtime.messages` table is partitioned by day. This allows old messages to be deleted performantly, by dropping old partitions. Partitions are retained for 3 days before being deleted.

Broadcast uses [Realtime Authorization](https://supabase.com/docs/guides/realtime/authorization) by default to protect your data.

## Streaming the Write-Ahead Log[#](#streaming-the-write-ahead-log)

A Postgres logical replication slot is acquired when connecting to your database.

Realtime delivers changes by polling the replication slot and appending channel subscription IDs to each wal record.

Subscription IDs are Erlang processes representing underlying sockets on the cluster. These IDs are globally unique and messages to processes are routed automatically by the Erlang virtual machine.

After receiving results from the polling query, with subscription IDs appended, Realtime delivers records to those clients.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/realtime/architecture.mdx)

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