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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# How to monitor Postgres and Supavisor connections

Last edited: 2/13/2025

* * *

This guide explains how connections impact your Supabase database's performance and how to optimize them for better resource utilization.

## Installing Supabase Grafana[#](#installing-supabase-grafana)

Supabase has an [open-source Grafana Repo](https://github.com/supabase/supabase-grafana) that displays real-time metrics of your database. Although the [Reports Dashboard](https://supabase.com/dashboard/project/_/reports) provides similar metrics, it averages the data by the hour or day. Having visuals of your connection usage can help you better allocate resources.

_Visual of Grafana Dashboard_

![image](https://github.com/supabase/supabase/assets/91111415/18ed2c88-332e-4e66-b9b4-c37e99a39104)

It can be run locally within Docker. Alternatively, you can deploy it to fly.io or Grafana Cloud, which are better for long-term data collection.

Installation instructions can be found in it the [metrics docs](https://supabase.com/docs/guides/platform/metrics#deploying-supabase-grafana)

## Observing connections[#](#observing-connections)

In Supabase Grafana, the "Client Connections" graph shows connections to both Supavisor and Postgres

![image](https://github.com/supabase/supabase/assets/91111415/141b8e01-9aae-4544-818c-acb47371ef3b)

-   **Yellow**: The yellow line represents the number of actively querying and idle connections to the Supavisor Pooler.
-   **Green**: The green line represents the total number of actively querying and idle direct connections to the database.

## Investigating connection sources[#](#investigating-connection-sources)

`pg_stat_activity` is a `VIEW` that keeps track of processes being run by your database, including connections. It's particularly useful for determining if idle clients are hogging connection slots.

This is a query you can use to observe the database roles and servers connecting to your database:

```
1234567891011121314SELECT   pg_stat_activity.pid,   ssl AS ssl_connection,   datname AS database,   usename AS connected_role,   application_name,   client_addr,   query,   query_start,   state,   backend_startFROM pg_stat_sslJOIN pg_stat_activity ON pg_stat_ssl.pid = pg_stat_activity.pid;
```

Interpreting the query:

| Column | Description |
| --- | --- |
| `pid` | connection id |
| `ssl` | Indicates if SSL is in use |
| `datname` | Name of the connected database (usually `postgres`) |
| `usename` | Role of the connected user |
| `application_name` | Name of the connecting application |
| `client_addr` | IP address of the connecting server |
| `query` | Last query executed by the connection |
| `query_start` | Time when the last query was executed |
| `state` | Querying state: active or idle |
| `backend_start` | Timestamp of the connection's establishment |

-   Note: If you are unfamiliar with the Supabase database roles, check this [reference](https://gist.github.com/TheOtherBrian1/d6e862a65e03049eb4f102f6ca809401)

If you believe a connection should be killed, you can do so by running the following query:

```
123select pg_terminate_backend(pid)  from pg_stat_activity  where pid = <connection_id>;
```

## Managing the Supavisor pooler:[#](#managing-the-supavisor-pooler)

The Supavisor Pooler is an intermediary between your clients (application servers) and the database. In transaction mode (port 6543), it can enable Postgres to share single connections with many clients, only allowing access when a query is pending. This prevents idle clients from hogging a direct connection and allows for more throughput.

In cases where you see significantly more pooler connections than direct connections, if you can, you should consider increasing how many direct connections the pooler is allowed to manage in the [Dashboard's Database Settings](https://supabase.com/dashboard/project/_/settings/database):

![image](https://github.com/supabase/supabase/assets/91111415/8e0cc80a-4d46-44b5-915b-8d7549f352d3).

The general rule is that if you are using the PostgREST database API, you should avoid raising your pool size past 40%. Otherwise, you can commit 80% to the pool. This leaves adequate room for the Authentication server and other utilities.

These numbers are generalizations and assume a certain level of activity from all connected servers. The actual values depend on your concurrent peak connection usage. For instance, if you were only using 80 connections in a week period and your database could support 500 connections, then realistically you could allocate the remaining 420 (minus a reasonable buffer) to service more demand.

## Secondary issues:[#](#secondary-issues)

When managing Postgres, outside of connections, there are generally 3 likely bottlenecks (links to address each):

-   [Disk/IO](https://github.com/orgs/supabase/discussions/27003)
-   [Memory](https://github.com/orgs/supabase/discussions/27021)
-   [CPU](https://github.com/orgs/supabase/discussions/27022)

They're all intertwined to some extent. If IO, CPU, or Memory are constrained, this can cause queries to slow down. Your application servers and Supavisor may compensate by creating more database connections or letting queries wait longer in their respective queues. Sometimes, by addressing or optimizing other factors of the database, you can better address connection issues.

## Other helpful resources:[#](#other-helpful-resources)

-   [Supavisor FAQ](https://github.com/orgs/supabase/discussions/21566)
-   [Using SQLAlchemy with Supabase](https://github.com/orgs/supabase/discussions/27071)
-   [Supabase and IPv4/IPv6 compatibility](https://github.com/orgs/supabase/discussions/27034)
-   [Addressing Max Client Errors](https://github.com/orgs/supabase/discussions/22305)
-   [Connecting to your database](https://supabase.com/docs/guides/database/connecting-to-postgres#integrations)
-   [How to Change Max Database Connections](https://github.com/orgs/supabase/discussions/27197)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Supavisor](https://supabase.com/docs/guides/troubleshooting?products=supavisor)

* * *

### Tags

[Grafana](https://supabase.com/docs/guides/troubleshooting?tags=Grafana)[connections](https://supabase.com/docs/guides/troubleshooting?tags=connections)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)[pooler](https://supabase.com/docs/guides/troubleshooting?tags=pooler)

* * *

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