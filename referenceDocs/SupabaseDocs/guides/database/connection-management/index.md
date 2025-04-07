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

Database

1.  [Database](https://supabase.com/docs/guides/database/overview)

3.  Working with your database (intermediate)

5.  [Managing connections](https://supabase.com/docs/guides/database/connection-management)

# 

Connection management

## 

Using your connections resourcefully

* * *

## Connections[#](#connections)

Every [Compute Add-On](https://supabase.com/docs/guides/platform/compute-add-ons) has a pre-configured direct connection count and Supavisor pool size. This guide discusses ways to observe and manage them resourcefully.

### Configuring Supavisor's pool size[#](#configuring-supavisors-pool-size)

You can change how many database connections Supavisor can manage by altering the pool size in the "Connection pooling configuration" section of the [Database Settings](https://supabase.com/dashboard/project/_/settings/database):

![Connection Info and Certificate.](https://supabase.com/docs/img/database/pool-size.png)

The general rule is that if you are heavily using the PostgREST database API, you should be conscientious about raising your pool size past 40%. Otherwise, you can commit 80% to the pool. This leaves adequate room for the Authentication server and other utilities.

These numbers are generalizations and depends on other Supabase products that you use and the extent of their usage. The actual values depend on your concurrent peak connection usage. For instance, if you were only using 80 connections in a week period and your database max connections is set to 500, then realistically you could allocate the difference of 420 (minus a reasonable buffer) to service more demand.

## Monitoring connections[#](#monitoring-connections)

### Capturing historical usage[#](#capturing-historical-usage)

Supabase offers a Grafana Dashboard that records and visualizes over 200 project metrics, including connections. For setup instructions, check the [metrics docs](https://supabase.com/docs/guides/platform/metrics).

Its "Client Connections" graph displays connections for both Supavisor and Postgres ![client connection graph](https://supabase.com/docs/img/database/grafana-connections.png)

### Observing live connections[#](#observing-live-connections)

`pg_stat_activity` is a special view that keeps track of processes being run by your database, including live connections. It's particularly useful for determining if idle clients are hogging connection slots.

Query to get all live connections:

```
1234567891011121314SELECT  pg_stat_activity.pid as connection_id,  ssl,  datname as database,  usename as connected_role,  application_name,  client_addr as IP,  query,  query_start,  state,  backend_startFROM pg_stat_sslJOIN pg_stat_activityON pg_stat_ssl.pid = pg_stat_activity.pid;
```

Interpreting the query:

| Column | Description |
| --- | --- |
| `connection_id` | connection id |
| `ssl` | Indicates if SSL is in use |
| `database` | Name of the connected database (usually `postgres`) |
| `usename` | Role of the connected user |
| `application_name` | Name of the connecting application |
| `client_addr` | IP address of the connecting server |
| `query` | Last query executed by the connection |
| `query_start` | Time when the last query was executed |
| `state` | Querying state: active or idle |
| `backend_start` | Timestamp of the connection's establishment |

The username can be used to identify the source:

| Role | API/Tool |
| --- | --- |
| `supabase_admin` | Used by Supabase for monitoring and by Realtime |
| `authenticator` | Data API (PostgREST) |
| `supabase_auth_admin` | Auth |
| `supabase_storage_admin` | Storage |
| `supabase_replication_admin` | Synchronizes Read Replicas |
| `postgres` | Supabase Dashboard and External Tools (e.g., Prisma, SQLAlchemy, PSQL...) |
| Custom roles defined by user | External Tools (e.g., Prisma, SQLAlchemy, PSQL...) |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/connection-management.mdx)

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