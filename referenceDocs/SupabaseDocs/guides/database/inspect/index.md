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

3.  Debugging

5.  [Debugging and monitoring](https://supabase.com/docs/guides/database/inspect)

# 

Debugging and monitoring

* * *

Database performance is a large topic and many factors can contribute. Some of the most common causes of poor performance include:

-   An inefficiently designed schema
-   Inefficiently designed queries
-   A lack of indexes causing slower than required queries over large tables
-   Unused indexes causing slow `INSERT`, `UPDATE` and `DELETE` operations
-   Not enough compute resources, such as memory, causing your database to go to disk for results too often
-   Lock contention from multiple queries operating on highly utilized tables
-   Large amount of bloat on your tables causing poor query planning

You can examine your database and queries for these issues using either the [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) or SQL.

## Using the CLI[#](#using-the-cli)

The Supabase CLI comes with a range of tools to help inspect your Postgres instances for potential issues. The CLI gets the information from [Postgres internals](https://www.postgresql.org/docs/current/internals.html). Therefore, most tools provided are compatible with any Postgres databases regardless if they are a Supabase project or not.

You can find installation instructions for the the Supabase CLI [here](https://supabase.com/docs/guides/cli).

### The `inspect db` command[#](#the-inspect-db-command)

The inspection tools for your Postgres database are under then `inspect db` command. You can get a full list of available commands by running `supabase inspect db help`.

```
123456789101112$ supabase inspect db helpTools to inspect your Supabase databaseUsage:  supabase inspect db [command]Available Commands:  bloat                Estimates space allocated to a relation that is full of dead tuples  blocking             Show queries that are holding locks and the queries that are waiting for them to be released  cache-hit            Show cache hit rates for tables and indices...
```

### Connect to any Postgres database[#](#connect-to-any-postgres-database)

Most inspection commands are Postgres agnostic. You can run inspection routines on any Postgres database even if it is not a Supabase project by providing a connection string via `--db-url`.

For example you can connect to your local Postgres instance:

```
1supabase --db-url postgresql://postgres:postgres@localhost:5432/postgres inspect db bloat
```

### Connect to a Supabase instance[#](#connect-to-a-supabase-instance)

Working with Supabase, you can link the Supabase CLI with your project:

```
1supabase link --project-ref <project-id>
```

Then the CLI will automatically connect to your Supabase project whenever you are in the project folder and you no longer need to provide `—db-url`.

### Inspection commands[#](#inspection-commands)

Below are the `db` inspection commands provided, grouped by different use cases.

Some commands might require `pg_stat_statements` to be enabled or a specific Postgres version to be used.

#### Disk storage[#](#disk-storage)

These commands are handy if you are running low on disk storage:

-   [bloat](https://supabase.com/docs/reference/cli/supabase-inspect-db-bloat) - estimates the amount of wasted space
-   [vacuum-stats](https://supabase.com/docs/reference/cli/supabase-inspect-db-vacuum-stats) - gives information on waste collection routines
-   [table-record-counts](https://supabase.com/docs/reference/cli/supabase-inspect-db-table-record-counts) - estimates the number of records per table
-   [table-sizes](https://supabase.com/docs/reference/cli/supabase-inspect-db-table-sizes) - shows the sizes of tables
-   [index-sizes](https://supabase.com/docs/reference/cli/supabase-inspect-db-index-sizes) - shows the sizes of individual index
-   [table-index-sizes](https://supabase.com/docs/reference/cli/supabase-inspect-db-table-index-sizes) - shows the sizes of indexes for each table

#### Query performance[#](#query-performance)

The commands below are useful if your Postgres database consumes a lot of resources like CPU, RAM or Disk IO. You can also use them to investigate slow queries.

-   [cache-hit](https://supabase.com/docs/reference/cli/supabase-inspect-db-cache-hit) - shows how efficient your cache usage is overall
-   [unused-indexes](https://supabase.com/docs/reference/cli/supabase-inspect-db-unused-indexes) - shows indexes with low index scans
-   [index-usage](https://supabase.com/docs/reference/cli/supabase-inspect-db-index-usage) - shows information about the efficiency of indexes
-   [seq-scans](https://supabase.com/docs/reference/cli/supabase-inspect-db-seq-scans) - show number of sequential scans recorded against all tables
-   [long-running-queries](https://supabase.com/docs/reference/cli/supabase-inspect-db-long-running-queries) - shows long running queries that are executing right now
-   [outliers](https://supabase.com/docs/reference/cli/supabase-inspect-db-outliers) - shows queries with high execution time but low call count and queries with high proportion of execution time spent on synchronous I/O

#### Locks[#](#locks)

-   [locks](https://supabase.com/docs/reference/cli/supabase-inspect-db-locks) - shows statements which have taken out an exclusive lock on a relation
-   [blocking](https://supabase.com/docs/reference/cli/supabase-inspect-db-blocking) - shows statements that are waiting for locks to be released

#### Connections[#](#connections)

-   [role-connections](https://supabase.com/docs/reference/cli/supabase-inspect-db-role-connections) - shows number of active connections for all database roles (Supabase-specific command)
-   [replication-slots](https://supabase.com/docs/reference/cli/supabase-inspect-db-replication-slots) - shows information about replication slots on the database

### Notes on `pg_stat_statements`[#](#notes-on-pgstatstatements)

Following commands require `pg_stat_statements` to be enabled: calls, locks, cache-hit, blocking, unused-indexes, index-usage, bloat, outliers, table-record-counts, replication-slots, seq-scans, vacuum-stats, long-running-queries.

When using `pg_stat_statements` also take note that it only stores the latest 5,000 statements. Moreover, consider resetting the analysis after optimizing any queries by running `select pg_stat_statements_reset();`

Learn more about pg\_stats [here](https://supabase.com/docs/guides/database/extensions/pg_stat_statements).

## Using SQL[#](#using-sql)

If you're seeing an `insufficient privilege` error when viewing the Query Performance page from the dashboard, run this command:

```
1$ grant pg_read_all_stats to postgres;
```

### Postgres cumulative statistics system[#](#postgres-cumulative-statistics-system)

Postgres collects data about its own operations using the [cumulative statistics system](https://www.postgresql.org/docs/current/monitoring-stats.html). In addition to this, every Supabase project has the [pg\_stat\_statements extension](https://supabase.com/docs/guides/database/extensions/pg_stat_statements) enabled by default. This extension records query execution performance details and is the best way to find inefficient queries. This information can be combined with the Postgres query plan analyzer to develop more efficient queries.

Here are some example queries to get you started.

### Most frequently called queries[#](#most-frequently-called-queries)

```
1234567891011121314151617181920select  auth.rolname,  statements.query,  statements.calls,  -- -- Postgres 13, 14, 15  statements.total_exec_time + statements.total_plan_time as total_time,  statements.min_exec_time + statements.min_plan_time as min_time,  statements.max_exec_time + statements.max_plan_time as max_time,  statements.mean_exec_time + statements.mean_plan_time as mean_time,  -- -- Postgres <= 12  -- total_time,  -- min_time,  -- max_time,  -- mean_time,  statements.rows / statements.calls as avg_rowsfrom  pg_stat_statements as statements  inner join pg_authid as auth on statements.userid = auth.oidorder by statements.calls desclimit 100;
```

This query shows:

-   query statistics, ordered by the number of times each query has been executed
-   the role that ran the query
-   the number of times it has been called
-   the average number of rows returned
-   the cumulative total time the query has spent running
-   the min, max and mean query times.

This provides useful information about the queries you run most frequently. Queries that have high `max_time` or `mean_time` times and are being called often can be good candidates for optimization.

### Slowest queries by execution time[#](#slowest-queries-by-execution-time)

```
1234567891011121314151617181920select  auth.rolname,  statements.query,  statements.calls,  -- -- Postgres 13, 14, 15  statements.total_exec_time + statements.total_plan_time as total_time,  statements.min_exec_time + statements.min_plan_time as min_time,  statements.max_exec_time + statements.max_plan_time as max_time,  statements.mean_exec_time + statements.mean_plan_time as mean_time,  -- -- Postgres <= 12  -- total_time,  -- min_time,  -- max_time,  -- mean_time,  statements.rows / statements.calls as avg_rowsfrom  pg_stat_statements as statements  inner join pg_authid as auth on statements.userid = auth.oidorder by max_time desclimit 100;
```

This query will show you statistics about queries ordered by the maximum execution time. It is similar to the query above ordered by calls, but this one highlights outliers that may have high executions times. Queries which have high or mean execution times are good candidates for optimization.

### Most time consuming queries[#](#most-time-consuming-queries)

```
123456789101112131415161718select  auth.rolname,  statements.query,  statements.calls,  statements.total_exec_time + statements.total_plan_time as total_time,  to_char(    (      (statements.total_exec_time + statements.total_plan_time) / sum(        statements.total_exec_time + statements.total_plan_time      ) over ()    ) * 100,    'FM90D0'  ) || '%' as prop_total_timefrom  pg_stat_statements as statements  inner join pg_authid as auth on statements.userid = auth.oidorder by total_time desclimit 100;
```

This query will show you statistics about queries ordered by the cumulative total execution time. It shows the total time the query has spent running as well as the proportion of total execution time the query has taken up.

Queries which are the most time consuming are not necessarily bad, you may have a very efficient and frequently ran queries that end up taking a large total % time, but it can be useful to help spot queries that are taking up more time than they should.

### Hit rate[#](#hit-rate)

Generally for most applications a small percentage of data is accessed more regularly than the rest. To make sure that your regularly accessed data is available, Postgres tracks your data access patterns and keeps this in its [shared\_buffers](https://www.postgresql.org/docs/15/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-MEMORY) cache.

Applications with lower cache hit rates generally perform more poorly since they have to hit the disk to get results rather than serving them from memory. Very poor hit rates can also cause you to burst past your [Disk IO limits](https://supabase.com/docs/guides/database/compute-add-ons#disk-io) causing significant performance issues.

You can view your cache and index hit rate by executing the following query:

```
123456789select  'index hit rate' as name,  (sum(idx_blks_hit)) / nullif(sum(idx_blks_hit + idx_blks_read), 0) * 100 as ratiofrom pg_statio_user_indexesunion allselect  'table hit rate' as name,  sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 as ratiofrom pg_statio_user_tables;
```

This shows the ratio of data blocks fetched from the Postgres [shared\_buffers](https://www.postgresql.org/docs/15/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-MEMORY) cache against the data blocks that were read from disk/OS cache.

If either of your index or table hit rate are < 99% then this can indicate your compute plan is too small for your current workload and you would benefit from more memory. [Upgrading your compute](https://supabase.com/docs/guides/database/compute-add-ons) is easy and can be done from your [project dashboard](https://supabase.com/dashboard/project/_/settings/compute-and-disk).

### Optimizing poor performing queries[#](#optimizing-poor-performing-queries)

Postgres has built in tooling to help you optimize poorly performing queries. You can use the [query plan analyzer](https://www.postgresql.org/docs/current/sql-explain.html) on any expensive queries that you have identified:

```
1explain analyze <query-statement-here>;
```

When you include `analyze` in the explain statement, the database attempts to execute the query and provides a detailed query plan along with actual execution times. So, be careful using `explain analyze` with `insert`/`update`/`delete` queries, because the query will actually run, and could have unintended side-effects.

If you run just `explain` without the `analyze` keyword, the database will only perform query planning without actually executing the query. This approach can be beneficial when you want to inspect the query plan without affecting the database or if you encounter timeouts in your queries.

Using the query plan analyzer to optimize your queries is a large topic, with a number of online resources available:

-   [Official docs.](https://www.postgresql.org/docs/current/using-explain.html)
-   [The Art of PostgreSQL.](https://theartofpostgresql.com/explain-plan-visualizer/)
-   [Postgres Wiki.](https://wiki.postgresql.org/wiki/Using_EXPLAIN)
-   [Enterprise DB.](https://www.enterprisedb.com/blog/postgresql-query-optimization-performance-tuning-with-explain-analyze)

You can pair the information available from `pg_stat_statements` with the detailed system metrics available [via your metrics endpoint](https://supabase.com/docs/guides/platform/metrics) to better understand the behavior of your DB and the queries you're executing against it.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/inspect.mdx)

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