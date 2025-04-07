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

# Diagnose HTTP API issues

Last edited: 2/3/2025

* * *

Symptoms of HTTP API issues include:

-   HTTP timeouts
-   5xx response codes
-   High response times

### Under-provisioned resources[#](#under-provisioned-resources)

The most common class of issues that causes HTTP timeouts and 5xx response codes is the under-provisioning of resources for your project. This can cause your project to be unable to service the traffic it is receiving.

Each Supabase project is provisioned with [segregated compute resources](https://supabase.com/docs/guides/platform/compute-add-ons). This allows the project to serve unlimited requests, as long as they can be handled using the resources that have been provisioned. Complex queries, or queries that process larger amounts of data, will require higher amounts of resources. As such, the amount of resources that can handle a high volume of simple queries (or queries involving small amounts of data), will likely be unable to handle a similar volume of complex queries.

You can view the resource utilization of your Supabase Project using the [reports in the Dashboard](https://supabase.com/dashboard/project/_/reports/database).

Some common solutions for this issue are:

-   [Upgrading](https://supabase.com/dashboard/project/_/settings/compute-and-disk) to a [larger compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons) in order to serve higher volumes of traffic.
-   [Optimizing the queries](https://supabase.com/docs/guides/platform/performance#examining-query-performance) being executed.
-   [Using fewer Postgres connections](https://supabase.com/docs/guides/platform/performance#configuring-clients-to-use-fewer-connections) can reduce the amount of resources needed on the project.
-   [Restarting](https://supabase.com/dashboard/project/_/settings/general) the project. This only temporarily solves the issue by terminating any ongoing workloads that might be tying up your compute resources.
    -   All databases of the project, including [Read replicas](https://supabase.com/docs/guides/platform/read-replicas), will be restarted.
    -   If you only want to restart a specific Read Replica, you can do so from the [Infrastructure Settings page](https://supabase.com/dashboard/project/_/settings/infrastructure).

If your [Disk IO budget](https://supabase.com/docs/guides/platform/compute-add-ons#disk-io) has been drained, you will need to either wait for it to be replenished the next day, or upgrade to a larger compute add-on to increase the budget available to your project.

## Unable to connect to your Supabase project[#](#unable-to-connect-to-your-supabase-project)

Symptom: You're unable to connect to your Postgres database directly, but can open the Project in the [Supabase Dashboard](https://supabase.com/dashboard/project/_/).

### Too many open connections[#](#too-many-open-connections)

Errors about too many open connections can be _temporarily_ resolved by [restarting the database](https://supabase.com/dashboard/project/_/settings/general). However, this won't solve the underlying issue for a permanent solution.

-   If you're receiving a `No more connections allowed (max_client_conn)` error:
    -   Configure your applications and services to [use fewer connections](https://supabase.com/docs/guides/platform/performance#configuring-clients-to-use-fewer-connections).
    -   [Upgrade](https://supabase.com/dashboard/project/_/settings/compute-and-disk) to a [larger compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons) to increase the number of available connections.
-   If you're receiving a `sorry, too many clients already` or `remaining connection slots are reserved for non-replication superuser connections` error message in addition to the above suggestions, switch to using the [connection pooler](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pool) instead.

### Connection refused[#](#connection-refused)

If you receive a `connection refused` error after a few initial failed connection attempts, your client has likely been temporarily blocked in order to protect the database from brute-force attacks. You can wait 30 minutes before trying again with the correct password, or you can [contact support](https://supabase.com/dashboard/support/new) with your client's IP address to manually unblock you.

If you're also unable to open the project using the [Supabase Dashboard](https://supabase.com/dashboard/project/_/), review the solutions for [under-provisioned projects](#under-provisioned-resources).

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Related error codes

[5xx](https://supabase.com/docs/guides/troubleshooting?errorCodes=5xx)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[API](https://supabase.com/docs/guides/troubleshooting?tags=API)[REST API](https://supabase.com/docs/guides/troubleshooting?tags=REST+API)[GraphQL](https://supabase.com/docs/guides/troubleshooting?tags=GraphQL)[HTTP](https://supabase.com/docs/guides/troubleshooting?tags=HTTP)

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