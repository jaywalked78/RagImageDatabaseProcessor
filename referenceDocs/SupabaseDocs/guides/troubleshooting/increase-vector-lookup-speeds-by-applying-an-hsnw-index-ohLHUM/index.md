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

# Increase vector lookup speeds by applying an HSNW index

Last edited: 2/4/2025

* * *

> Although this guide is specifically for HNSW indexes, it can be generalized to work for any index type

> Building an index without the `CONCURRENTLY` modifier will lock the table, but it will also increase build times. For general advice about indexes, check out this [guide](https://github.com/orgs/supabase/discussions/22449).

### **To speed up queries, it is ideal to create an HSNW index on your embedded column**[#](#to-speed-up-queries-it-is-ideal-to-create-an-hsnw-index-on-your-embedded-column)

The general structure for creating an HNSW index follows this pattern:

```
1CREATE INDEX <custom name of index> ON <table name> USING hnsw (<vectorized column> <search type>);
```

Search can be one of three types:

| operator | description | search type |
| --- | --- | --- |
| `<->` | Euclidean distance | vector\_l2\_ops |
| `<#>` | negative inner product | vector\_ip\_ops |
| `<=>` | cosine distance | vector\_cosine\_ops |

Queries can only utilize the index if it matches the search type used. If you are unsure which search type to prioritize, vector\_cosine\_ops is the most commonly used. You can checkout our [guide](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes) for more info. The folks at Crunchy Data also wrote an [explainer](https://www.crunchydata.com/blog/hnsw-indexes-with-postgres-and-pgvector) that you may find useful.

Applying an index can be slow and computationally expensive, so there are a few preparations that should be made beforehand:

**1\. Make sure your pgvector is the latest available version on Supabase.**

Versions 0.6 and later have accelerated HNSW build speeds. You can observe your current version in the [Dashboard's Extensions Page](https://supabase.com/dashboard/project/_/database/extensions). You can perform a software upgrade in the [Infrastructure Settings](https://supabase.com/dashboard/project/_/settings/infrastructure) if necessary.

**2\. Setting up an external connection**

The Dashboard has an internal time limit of ~2 minutes for queries. Indexing a large table will almost always take more time, so it is necessary to execute your code through an external interface, such as PSQL.

You can install PSQL in [macOS](https://stackoverflow.com/a/49689589/2188186) and [Windows](https://www.postgresql.org/download/windows/) by following these links and instructions. For Linux (Debian) you can run the following:

```
12sudo apt-get updatesudo apt-get install postgresql-client
```

Once installed, you can find your PSQL string from the [Database Settings](https://supabase.com/dashboard/project/_/settings/database), which can be executed in the terminal to create a psql session.

If your network can use IPv6, consider using the direct connection string instead of Supavisor. It's not mandatory, but for tasks that run a long time, it's best to reduce network complexity. To check if your network is compatible, use this cURL command to request your IPv6 address:

```
1curl -6 https://ifconfig.co/ip
```

If an address is returned, you should be able to use your direct connection string found in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database):

**3\. Increase memory for index creation (optional)**

The `maintance_work_mem` variable limits the maximum amount of memory that can be used by maintenance operations, such as vacuuming, altering, and indexing tables. In your session you should try to set it to a reasonably high value:

```
1set maintenance_work_mem to <several Gb's>; -- '#GB'
```

Inspect value to make sure it has been set:

```
1show maintenance_work_mem;
```

**4\. Increase cores for index creation (optional)**

The `max_parallel_maintenance_workers` variable limits the amount of cores that can be used by maintenance operations, including indexing tables. In your session, you should try to set it to a value roughly 1/2 to 2/3s of your [compute core amount](https://supabase.com/docs/guides/platform/compute-add-ons):

```
1set max_parallel_maintenance_workers to <integer>;
```

Inspect value to make sure it has been set:

```
1show max_parallel_maintenance_workers;
```

**5\. Setting a custom timeout**

Disable query timeout for your connection:

```
1set statement_timeout = '0';
```

Inspect value to make sure it has been set:

```
1show statement_timeout;
```

**6\. Consider temporarily upgrading your compute size (optional)**

If your task is particularly long, you can speed it up by boosting your computing power temporarily. Compute size is charged by the hour, so you can increase it for an hour or two to finish your task faster, then scale it back afterwards. Here is a list of [compute add-ons](https://supabase.com/docs/guides/platform/compute-add-ons). If you want to temporarily upgrade, you can find the add-ons for your project in your [Dashboard's Add-ons Settings.](https://supabase.green/dashboard/project/_/settings/addons)

**7\. Consider increasing disk size (optional)**

HSNW indexes can produce temporary files during their construction that may consume a few GBs worth of disk. Consider increasing the disk size in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) to accommodate for short-term disk stress.

![Screenshot 2024-06-10 at 8 00 28 PM](https://github.com/supabase/supabase/assets/91111415/9820e214-8796-4b56-91a3-2e73e4836b2f)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Ai](https://supabase.com/docs/guides/troubleshooting?products=ai)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[index](https://supabase.com/docs/guides/troubleshooting?tags=index)[hnsw](https://supabase.com/docs/guides/troubleshooting?tags=hnsw)[vector](https://supabase.com/docs/guides/troubleshooting?tags=vector)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)[speed](https://supabase.com/docs/guides/troubleshooting?tags=speed)

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