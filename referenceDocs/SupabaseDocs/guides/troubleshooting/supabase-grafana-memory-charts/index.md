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

# Interpreting Supabase Grafana Memory Charts

Last edited: 2/21/2025

* * *

> [Supabase Grafana Installation Guide](https://supabase.com/docs/guides/platform/metrics#deploying-supabase-grafana)

Here are examples of unhealthy memory usage: ![image](https://github.com/supabase/supabase/assets/91111415/baebfc74-642d-4988-992c-bb0f473a05ad) ![image](https://github.com/supabase/supabase/assets/91111415/b95c83cf-aa98-4b50-8e07-29f57aaa676c)

-   **Yellow**: represents active memory
-   **Red**: represents SWAP, which is disk storage that the system treats as if it were actually memory
-   **Green**: it is unclaimed (the system will always leave some memory unclaimed)
-   **Blue**: it is cached data and a buffer

The cache in Postgres is important because the database will store frequently accessed data in it for rapid retrieval. If too much active memory is needed, it runs the risk of excessively displacing cache. This will force queries to check disk, which is slow.

Most data in a database is idle, but in cases where there is little available memory or uncached data is rapidly accessed, [thrashing](https://en.wikipedia.org/wiki/Thrashing_\(computer_science\)) can occur.

Ideally, you want queries to hit the cache 99% of the time. You can use the [Supabase CLI](https://supabase.com/docs/guides/database/inspect) `inspect db cache hit` command to check your cache hit rate. Alternatively, you can run the [query](https://github.com/supabase/cli/blob/c9cce58025fded16b4c332747f819a44f45c3b83/internal/inspect/bloat/bloat.go#L17) found in the CLI's GitHub repo in the [SQL Editor](https://supabase.com/dashboard/project/_/sql/)

```
1234567891011# login to the CLInpx supabase login# initlize a local supabase directorynpx supabase init#link your projectnpx supabase link# find cache hit ratenpx supabase inspect db cache-hit --linked
```

If the cache hit rate begins to drop below the ideal amount, one should consider taking the following actions:

Optimizing:

1.  [Apply indexes](https://github.com/orgs/supabase/discussions/22449): can reduce the amount of data pulled from disk into memory
2.  [Increasing the compute size](https://supabase.com/docs/guides/platform/compute-add-ons)
3.  [Distribute load by using read-replicas](https://supabase.com/dashboard/project/_/settings/infrastructure)
4.  [Partitions](https://supabase.com/docs/guides/database/partitions): Generally should be used on _very_ large tables to minimize data pulled from disk into memory
5.  [Remove bloat](https://supabase.com/docs/guides/database/bloat): Bloat can fragment data across pages, causing redundant data to be pulled from disk.
6.  Table refactoring: Split tables to isolate columns that are less frequently accessed, so they are not redundantly pulled into memory while accessing hotter data

### Other useful Supabase Grafana guides:[#](#other-useful-supabase-grafana-guides)

-   [Connections](https://github.com/orgs/supabase/discussions/27141)
-   [Disk](https://github.com/orgs/supabase/discussions/27003)
-   [CPU](https://github.com/orgs/supabase/discussions/27022)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[Grafana](https://supabase.com/docs/guides/troubleshooting?tags=Grafana)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)[memory](https://supabase.com/docs/guides/troubleshooting?tags=memory)

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