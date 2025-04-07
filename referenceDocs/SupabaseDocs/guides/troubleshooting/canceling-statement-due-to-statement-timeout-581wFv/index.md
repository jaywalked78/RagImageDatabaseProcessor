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

# Canceling statement due to "statement timeout"

Last edited: 2/4/2025

* * *

> If encountering 504 or timeout errors in the Dashboard, check out this [guide](https://github.com/orgs/supabase/discussions/21133#discussioncomment-9573776)

You can run this query to check the current settings set for your roles: `SELECT rolname, rolconfig FROM   pg_roles;`

To increase the `statement_timeout` for a specific role, you may follow the instructions [here](https://supabase.com/docs/guides/database/timeouts#changing-the-default-timeout). Note that it may require a quick reboot for the changes to take effect.

Additionally, to check how long a query is taking, you can check the Query Performance report which can give you more information on the query's performance: [https://app.supabase.com/project/\_/reports/query-performance](https://app.supabase.com/project/_/reports/query-performance). You can use the [query plan analyzer](https://www.postgresql.org/docs/current/sql-explain.html) on any expensive queries that you have identified: `explain analyze <query-statement-here>;`. For supabase-js/ PostgREST queries you can use `.explain()`.

You can also make use of Postgres logs that will give you useful information like when the query was executed: [https://app.supabase.com/project/\_/logs/postgres-logs](https://app.supabase.com/project/_/logs/postgres-logs).

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[statement](https://supabase.com/docs/guides/troubleshooting?tags=statement)[timeout](https://supabase.com/docs/guides/troubleshooting?tags=timeout)[postgres](https://supabase.com/docs/guides/troubleshooting?tags=postgres)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)

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