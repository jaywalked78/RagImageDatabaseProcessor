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

3.  Examples

5.  [Replicating from Supabase to External Postgres](https://supabase.com/docs/guides/database/postgres/setup-replication-external)

# 

Replicate to another Postgres database using Logical Replication

* * *

For this example, you will need:

-   A Supabase project
-   A Postgres database (running v10 or newer)

You will be running commands on both of these databases to publish changes from the Supabase database to the external database.

1.  Create a `publication` on the **Supabase database**:

```
1CREATE PUBLICATION example_pub;
```

2.  Also on the **Supabase database**, create a `replication slot`:

```
1select pg_create_logical_replication_slot('example_slot', 'pgoutput');
```

3.  Now we will connect to our **external database** and subscribe to our `publication` Note: ):

This will need a direct connection to your database and you can find the connection info in the [Dashboard](https://supabase.com/dashboard/project/_/settings/database).

You will also need to ensure that ipv6 is supported by your replication destination.

If you would prefer not to use the `postgres` user, then you can run `CREATE ROLE <user> WITH REPLICATION;` using the `postgres` user.

```
1234CREATE SUBSCRIPTION example_subCONNECTION 'host=db.oaguxblfdassqxvvwtfe.supabase.co user=postgres password=YOUR_PASS dbname=postgres'PUBLICATION example_pubWITH (copy_data = true, create_slot=false, slot_name=example_slot);
```

`create_slot` is set to `false` because `slot_name` is provided and the slot was already created in Step 2. To copy data from before the slot was created, set `copy_data` to `true`.

4.  Add all the tables that you want replicated to the publication.

```
1ALTER PUBLICATION example_pub ADD TABLE example_table;
```

5.  Check the replication status using `pg_stat_replication`

```
1select * from pg_stat_replication;
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/setup-replication-external.mdx)

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