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

# Disabling Prepared statements

Last edited: 2/4/2025

* * *

### It is important to note that although the direct connections and Supavisor in session mode support prepared statements, Supavisor in transaction mode does not.[#](#it-is-important-to-note-that-although-the-direct-connections-and-supavisor-in-session-mode-support-prepared-statements-supavisor-in-transaction-mode-does-not)

## How to disable prepared statements for Supavisor in transaction mode[#](#how-to-disable-prepared-statements-for-supavisor-in-transaction-mode)

Each ORM or library configures prepared statements differently. Here are settings for some common ones. If you don't see yours, make a comment

# Prisma:

add ?pgbouncer=true to end of connection string:

```
1postgres://[db-user].[project-ref]:[db-password]@aws-0-[aws-region].pooler.supabase.com:6543/[db-name]?pgbouncer=true
```

# Drizzle:

Add a prepared false flag to the client:

```
1export const client = postgres(connectionString, { prepare: false })
```

# Node Postgres

[Just omit the "name" value in a query definition](https://node-postgres.com/features/queries#prepared-statements):

```
12345const query = {  name: 'fetch-user', // <--------- DO NOT INCLUDE  text: 'SELECT * FROM user WHERE id = $1',  values: [1],}
```

# Psycopg

set the [prepare\_threshold](https://www.psycopg.org/psycopg3/docs/api/connections.html#psycopg.Connection.prepare_threshold) to `None`.

# asyncpg

Follow the recommendation in the [asyncpg docs](https://magicstack.github.io/asyncpg/current/faq.html#why-am-i-getting-prepared-statement-errors)

> disable automatic use of prepared statements by passing `statement_cache_size=0` to [asyncpg.connect()](https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.connect) and [asyncpg.create\_pool()](https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.pool.create_pool) (and, obviously, avoid the use of [Connection.prepare()](https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.prepare));

# Rust's Deadpool or `tokio-postgres`:

-   Check [GitHub Discussion](https://github.com/bikeshedder/deadpool/issues/340#event-13642472475)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Supavisor](https://supabase.com/docs/guides/troubleshooting?products=supavisor)

* * *

### Tags

[prepared](https://supabase.com/docs/guides/troubleshooting?tags=prepared)[statements](https://supabase.com/docs/guides/troubleshooting?tags=statements)[transaction](https://supabase.com/docs/guides/troubleshooting?tags=transaction)[mode](https://supabase.com/docs/guides/troubleshooting?tags=mode)[disable](https://supabase.com/docs/guides/troubleshooting?tags=disable)

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