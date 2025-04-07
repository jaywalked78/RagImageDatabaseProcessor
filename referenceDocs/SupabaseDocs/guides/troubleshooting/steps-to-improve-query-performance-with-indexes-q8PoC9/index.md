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

# Steps to improve query performance with indexes

Last edited: 2/21/2025

* * *

# Optimizing your database

This is an intermediate and actionable guide for Postgres optimization within the Supabase ecosystem.

> Consider checking out [Index\_advisor](https://supabase.com/docs/guides/database/extensions/index_advisor) and the [performance advisor](https://supabase.com/dashboard/project/_/database/performance-advisor) now available in the Dashboard!

## Installing Supabase Grafana[#](#installing-supabase-grafana)

Supabase has an [open-source Grafana Repo](https://github.com/supabase/supabase-grafana) that displays real-time metrics of your database. Although the [Reports Dashboard](https://supabase.com/dashboard/project/_/reports) provides similar metrics, it averages the data by the hour or day. Having visibility over how your database responds to changes helps to ensure that the database is not stressed by the index-building process.

_Visual of Grafana Dashboard_ ![image](https://supabase.com/docs/img/troubleshooting/18ed2c88-332e-4e66-b9b4-c37e99a39104.png)

It can be run locally within Docker or can be deployed for free to fly.io. Installation instructions can be found in [Supabase's metrics docs](https://supabase.com/docs/guides/platform/metrics#deploying-supabase-grafana)

## Query optimization through indexes[#](#query-optimization-through-indexes)

Disk (storage) is relatively slow compared to memory, so Postgres will take frequently accessed data and cache it in memory for fast access.

Ideally, you want the cache hit rate (cache-hits/total-hits) to be 99%. You should try to run the following query on your instance:

```
123456789select  'index hit rate' as name,  (sum(idx_blks_hit)) / nullif(sum(idx_blks_hit + idx_blks_read), 0) as ratiofrom pg_statio_user_indexesunion allselect  'table hit rate' as name,  sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) as ratiofrom pg_statio_user_tables;
```

If the cache hit rate is relatively low, it often means that you need to increase your memory capacity. The second metric that is often inspected is index usage. Indexes are data structures that allow Postgres to search for information quickly - think of them like you would think of an index at the back of a book. Instead of scanning every page (or row), you can use an index to find the contents you need quickly. For a better understanding of how Postgres decides on whether to use an index or not, check out this [explainer](https://github.com/orgs/supabase/discussions/26959).

The index hit rate (how often an index is used) can usually be improved moderately.

There's a query to find out how often an index is used when accessing a table:

```
1234567select  relname,  100 * idx_scan / (seq_scan + idx_scan) as percent_of_times_index_used,  n_live_tup as rows_in_tablefrom pg_stat_user_tableswhere seq_scan + idx_scan > 0order by n_live_tup desc;
```

A lot of the [queries for inspecting performance](https://supabase.com/docs/reference/cli/supabase-inspect-db) are actually pre-bundled as part of the [Supabase CLI](https://supabase.com/docs/guides/cli/getting-started). For instance, there is a command for testing which indexes of yours are unnecessary and are needlessly taking up space:

```
12345npx supabase loginnpx supabase linknpx supabase inspect db unused-indexes
```

There is an extension called [index\_advisor](https://supabase.com/docs/guides/database/extensions/index_advisor) that creates virtual indexes on your queries and then checks which ones increase performance the best. Unlike normal index creation, virtual indexes can be made rapidly, which makes uncovering the most performant solutions fast. The [Query Performance Advisor](https://supabase.com/dashboard/project/_/database/query-performance) in the Dashboard is configured to use index\_advisor to make optimization suggestions and you should check it out to see where you can improve.

Index\_advisor won't test indexes added through extensions nor will it test GIN/GIST indexes. For JSON or ARRAY columns, consider exploring GIN/GIST indexes separately from index\_advisor. If you're using pg\_vector, it's crucial to use an [HSNW index](https://github.com/orgs/supabase/discussions/21379).

Indexes can significantly speed up reads, sometimes boosting performance by 100 times. However, they come with a trade-off: they need to track all column changes, which can slow down data-modifying queries like UPDATEs, DELETEs, and INSERTs.

Generally, indexes offer more benefits. For example, primary key columns automatically have a B-Tree index, enhancing read and join operations without significantly affecting write queries. Nonetheless, it's wise to avoid carelessly adding indexes.

Some indexes may take a long time to build. A [guide](https://github.com/orgs/supabase/discussions/21379) was written for applying HSNW indexes, but it can be generalized and referenced for applying others, too.

When building an index, the affected table is locked, preventing write operations. If this poses an issue, use the [`CONCURRENTLY` modifier](https://www.postgresql.org/docs/current/sql-createindex.html). However, reserve this for necessary cases only, as it entails building the index twice, prolonging the process and increasing computational costs.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Cli](https://supabase.com/docs/guides/troubleshooting?products=cli)

* * *

### Tags

[indexes](https://supabase.com/docs/guides/troubleshooting?tags=indexes)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)[optimization](https://supabase.com/docs/guides/troubleshooting?tags=optimization)[grafana](https://supabase.com/docs/guides/troubleshooting?tags=grafana)[query](https://supabase.com/docs/guides/troubleshooting?tags=query)

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