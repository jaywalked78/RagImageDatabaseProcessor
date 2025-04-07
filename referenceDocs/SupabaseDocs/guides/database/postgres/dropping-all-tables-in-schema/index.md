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

5.  [Drop All Tables in Schema](https://supabase.com/docs/guides/database/postgres/dropping-all-tables-in-schema)

# 

Drop all tables in a PostgreSQL schema

* * *

Execute the following query to drop all tables in a given schema. Replace `my-schema-name` with the name of your schema. In Supabase, the default schema is `public`.

This deletes all tables and their associated data. Ensure you have a recent [backup](https://supabase.com/docs/guides/platform/backups) before proceeding.

```
1234567do $$ declare    r record;begin    for r in (select tablename from pg_tables where schemaname = 'my-schema-name') loop        execute 'drop table if exists ' || quote_ident(r.tablename) || ' cascade';    end loop;end $$;
```

This query works by listing out all the tables in the given schema and then executing a `drop table` for each (hence the `for... loop`).

You can run this query using the [SQL Editor](https://supabase.com/dashboard/project/_/sql) in the Supabase Dashboard, or via `psql` if you're [connecting directly to the database](https://supabase.com/docs/guides/database/connecting-to-postgres#direct-connections).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/dropping-all-tables-in-schema.mdx)

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