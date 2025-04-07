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

3.  Extensions

5.  [pg\_stat\_statements: SQL Planning and Execution Statistics](https://supabase.com/docs/guides/database/extensions/pg_stat_statements)

# 

pg\_stat\_statements: Query Performance Monitoring

* * *

`pg_stat_statements` is a database extension that exposes a view, of the same name, to track statistics about SQL statements executed on the database. The following table shows some of the available statistics and metadata:

| Column Name | Column Type | Description |
| --- | --- | --- |
| `userid` | `oid` (references `pg_authid.oid`) | OID of user who executed the statement |
| `dbid` | `oid` (references `pg_database.oid`) | OID of database in which the statement was executed |
| `toplevel` | `bool` | True if the query was executed as a top-level statement (always true if pg\_stat\_statements.track is set to top) |
| `queryid` | `bigint` | Hash code to identify identical normalized queries. |
| `query` | `text` | Text of a representative statement |
| `plans` | `bigint` | Number of times the statement was planned (if pg\_stat\_statements.track\_planning is enabled, otherwise zero) |
| `total_plan_time` | `double precision` | Total time spent planning the statement, in milliseconds (if pg\_stat\_statements.track\_planning is enabled, otherwise zero) |
| `min_plan_time` | `double precision` | Minimum time spent planning the statement, in milliseconds (if pg\_stat\_statements.track\_planning is enabled, otherwise zero) |

A full list of statistics is available in the [pg\_stat\_statements docs](https://www.postgresql.org/docs/current/pgstatstatements.html).

For more information on query optimization, check out the [query performance guide](https://supabase.com/docs/guides/platform/performance#examining-query-performance).

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "pg\_stat\_statements" and enable the extension.

## Inspecting activity[#](#inspecting-activity)

A common use for `pg_stat_statements` is to track down expensive or slow queries. The `pg_stat_statements` view contains a row for each executed query with statistics inlined. For example, you can leverage the statistics to identify frequently executed and slow queries against a given table.

```
12345678910111213141516select	calls,	mean_exec_time,	max_exec_time,	total_exec_time,	stddev_exec_time,	queryfrom	pg_stat_statementswhere    calls > 50                   -- at least 50 calls    and mean_exec_time > 2.0     -- averaging at least 2ms/call    and total_exec_time > 60000  -- at least one minute total server time spent    and query ilike '%user_in_organization%' -- filter to queries that touch the user_in_organization tableorder by	calls desc
```

From the results, we can make an informed decision about which queries to optimize or index.

## Resources[#](#resources)

-   Official [pg\_stat\_statements documentation](https://www.postgresql.org/docs/current/pgstatstatements.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_stat_statements.mdx)

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