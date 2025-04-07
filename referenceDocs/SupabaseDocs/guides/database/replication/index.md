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

3.  Configuration, optimization, and testing

5.  [Managing database replication](https://supabase.com/docs/guides/database/replication)

# 

Replication

* * *

Replication is a technique for copying the data from one database to another. Supabase uses replication functionality to provide a real-time API. Replication is useful for:

-   Spreading out the "load." For example, if your database has a lot of reads, you might want to split it between two databases.
-   Reducing latency. For example, you may want one database in London to serve your European customers, and one in New York to serve the US.

Replication is done through _publications_, a method of choosing which changes to send to other systems (usually another Postgres database). Publications can be managed in the [Dashboard](https://supabase.com/dashboard) or with SQL.

## Manage publications in the dashboard[#](#manage-publications-in-the-dashboard)

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Publications** in the sidebar.
3.  Control which database events are sent by toggling **Insert**, **Update**, and **Delete**.
4.  Control which tables broadcast changes by selecting **Source** and toggling each table.

## Create a publication[#](#create-a-publication)

This publication contains changes to all tables.

```
12create publication publication_namefor all tables;
```

## Create a publication to listen to individual tables[#](#create-a-publication-to-listen-to-individual-tables)

```
12create publication publication_namefor table table_one, table_two;
```

## Add tables to an existing publication[#](#add-tables-to-an-existing-publication)

```
12alter publication publication_nameadd table table_name;
```

## Listen to `insert`[#](#listen-to-insert)

```
123create publication publication_namefor all tableswith (publish = 'insert');
```

## Listen to `update`[#](#listen-to-update)

```
123create publication publication_namefor all tableswith (publish = 'update');
```

## Listen to `delete`[#](#listen-to-delete)

```
123create publication publication_namefor all tableswith (publish = 'delete');
```

## Remove a publication[#](#remove-a-publication)

```
1drop publication if exists publication_name;
```

## Recreate a publication[#](#recreate-a-publication)

If you're recreating a publication, it's best to do it in a transaction to ensure the operation succeeds.

```
1234567begin;  -- remove the realtime publication  drop publication if exists publication_name;  -- re-create the publication but don't enable it for any tables  create publication publication_name;commit;
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/replication.mdx)

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