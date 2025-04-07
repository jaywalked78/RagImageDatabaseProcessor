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

# Partitioning an existing table with same name

Last edited: 2/4/2025

* * *

Our documentation on table partitioning here: [https://supabase.com/docs/guides/database/partitions](https://supabase.com/docs/guides/database/partitions)

Read the below information if you want the partitioned table to retain the name of the original table.

-   You can create empty "parent" partitioned table using CREATE TABLE parent\_table LIKE source\_table \[ like\_option ... \] PARTITION BY ...

LIKE option will copy column definitions, constraints etc. from source table automatically. For different like\_options see [https://www.postgresql.org/docs/current/sql-createtable.html](https://www.postgresql.org/docs/current/sql-createtable.html) (you could try INCLUDING ALL like option).

-   Then you can create empty partitions for ranges that you like.
    
-   Then you could insert rows from the old/original table into parent\_table. They will be spread into partitions at almost no cost. But the process could take time. For experiment, you could insert a subset from original table (using `ORDER BY id LIMIT <number>` clause) and see time needed to do actual work.
    
-   It's crucial to check that you haven't forgotten some range by checking default partition (that contains rows inserted into a parent table but not corresponding any partition ranges) meanwhile. Overgrown default partition slows down almost any operations with partitioned table.
    
-   When insert is finished you can rename old and new "parent" table. Do it in one transaction, so that you have no time old name is already don't exist but not yet re-created for any query.
    
-   Indices definition will be copied with INCLUDING ALL option. They will be propagated during insertion of data into a new parent table.
    
-   Of course you can hold old table for your data to be safe indefinitely. Do not delete it outright! Your queries after renaming will not use it. Indexes etc. work behind the scenes, you are not required to know its names. (In reality indices for a "new" partitioned table will be new, but you won't see it if you have used `LIKE..INCLUDING ALL` option).
    
-   Triggers will be needed to re-create for "parent" partitioned table using `CREATE TRIGGER` clause [https://www.postgresql.org/docs/16/sql-createtrigger.html](https://www.postgresql.org/docs/16/sql-createtrigger.html)
    
-   Functions will switch to work with a new table after renaming.
    
-   There are certain limitations of declarative partitioning that you may need to be aware: [https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITIONING-DECLARATIVE](https://www.postgresql.org/docs/current/ddl-partitioning.html#DDL-PARTITIONING-DECLARATIVE)
    

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[partitioning](https://supabase.com/docs/guides/troubleshooting?tags=partitioning)[table](https://supabase.com/docs/guides/troubleshooting?tags=table)[postgresql](https://supabase.com/docs/guides/troubleshooting?tags=postgresql)[constraint](https://supabase.com/docs/guides/troubleshooting?tags=constraint)[index](https://supabase.com/docs/guides/troubleshooting?tags=index)

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