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

3.  More

5.  [Prisma](https://supabase.com/docs/guides/database/prisma)

7.  [Prisma troubleshooting](https://supabase.com/docs/guides/database/prisma/prisma-troubleshooting)

# 

Troubleshooting prisma errors

* * *

This guide addresses common Prisma errors that you might encounter while using Supabase.

A full list of errors can be found in [Prisma's official docs](https://www.prisma.io/docs/orm/reference/error-reference).

## Understanding connection string parameters: [#](#start)

Unlike other libraries, Prisma lets you configure [its settings](https://www.prisma.io/docs/orm/overview/databases/postgresql#arguments) through special options appended to your connection string.

These options, called "query parameters," can be used to address specific errors.

```
123# Example of query parametersconnection_string.../postgres?KEY1=VALUE&KEY2=VALUE&KEY3=VALUE
```

# Errors

## ... prepared statement already exists[#](#-prepared-statement-already-exists)

Supavisor in transaction mode (port 6543) does not support [prepared statements](https://www.postgresql.org/docs/current/sql-prepare.html), which Prisma will try to create in the background.

### Solution: [#](#solution-prepared-statement-exists)

-   Add `pgbouncer=true` to the connection string. This turns off prepared statements in Prisma.

```
1.../postgres?pgbouncer=true
```

* * *

## Can't reach database server at:[#](#cant-reach-database-server-at)

Prisma couldn't establish a connection with Postgres or Supavisor before the timeout

### Possible causes: [#](#possible-causes-cant-reach-database-server-at)

-   **Database overload**: The database server is under heavy load, causing Prisma to struggle to connect.
-   **Malformed connection string**: The connection string used by Prisma is incorrect or incomplete.
-   **Transient network issues**: Temporary network problems are disrupting the connection.

### Solutions: [#](#solution-cant-reach-database-server-at)

-   **Check database health**: Use the [Reports Dashboard](https://supabase.com/dashboard/project/_/reports/database) to monitor CPU, memory, and I/O usage. If the database is overloaded, consider increasing your [compute size](https://supabase.com/docs/guides/platform/compute-add-ons) or [optimizing your queries](https://supabase.com/docs/guides/database/query-optimization).
-   **Verify connection string**: Double-check the connection string in your Prisma configuration to ensure it matches one in your [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
-   **Increase connection timeout**: Try increasing the `connect_timeout` parameter in your Prisma configuration to give it more time to establish a connection.

```
1.../postgres?connect_timeout=30
```

* * *

## Timed out fetching a new connection from the connection pool:[#](#timed-out-fetching-a-new-connection-from-the-connection-pool)

Prisma is unable to allocate connections to pending queries fast enough to meet demand.

### Possible causes: [#](#possible-causes-timed-out-fetching-a-new-connection)

-   **Overwhelmed server**: The server hosting Prisma is under heavy load, limiting its ability to manage connections. By default, Prisma will create the default `num_cpus * 2 + 1` worth of connections. A common cause for server strain is increasing the `connection_limit` significantly past the default.
-   **Insufficient pool size**: The Supavisor pooler does not have enough connections available to quickly satisfy Prisma's requests.
-   **Slow queries**: Prisma's queries are taking too long to execute, preventing it from releasing connections for reuse.

### Solutions: [#](#solution-timed-out-fetching-a-new-connection)

-   **Increase the pool timeout**: Increase the `pool_timeout` parameter in your Prisma configuration to give the pooler more time to allocate connections.
-   **Reduce the connection limit**: If you've explicitly increased the `connection_limit` parameter in your Prisma configuration, try reducing it to a more reasonable value.
-   **Increase pool size**: If you are connecting with Supavisor, try increasing the pool size in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
-   **Optimize queries**: [Improve the efficiency of your queries](https://supabase.com/docs/guides/database/query-optimization) to reduce execution time.
-   **Increase compute size**: Like the preceding option, this is a strategy to reduce query execution time.

* * *

## Server has closed the connection[#](#server-has-closed-the-connection)

According to this [GitHub Issue for Prisma](https://github.com/prisma/prisma/discussions/7389), this error may be related to large return values for queries. It may also be caused by significant database strain.

### Solutions: [#](#solution-server-has-closed-the-connection)

-   **Limit row return sizes**: Try to limit the total amount of rows returned for particularly large requests.
-   **Minimize database strain**:Check the Reports Page for database strain. If there is obvious strain, consider [optimizing](https://supabase.com/docs/guides/database/query-optimization) or increasing compute size

* * *

## Drift detected: Your database schema is not in sync with your migration history[#](#drift-detected-your-database-schema-is-not-in-sync-with-your-migration-history)

Prisma relies on migration files to ensure your database aligns with Prisma's model. External schema changes are detected as "drift", which Prisma will try to overwrite, potentially causing data loss.

### Possible causes: [#](#possible-causes-your-database-schema-is-not-in-sync)

-   **Supabase Managed Schemas**: Supabase may update managed schemas like auth and storage to introduce new features. Granting Prisma access to these schemas can lead to drift during updates.
-   **External Schema Modifications**: Your team or another tool might have modified the database schema outside of Prisma, causing drift.

### Solution: [#](#solution-your-database-schema-is-not-in-sync)

-   **Baselining migrations**: [baselining](https://www.prisma.io/docs/orm/prisma-migrate/workflows/baselining) re-syncs Prisma by capturing the current database schema as the starting point for future migrations.

* * *

## Max client connections reached[#](#max-client-connections-reached)

Postgres or Supavisor rejected a request for more connections

### Possible causes:[#](#possible-causes-max-client-connections-reached)

-   **When working in transaction mode (port 6543):** The error "Max client connections reached" occurs when clients try to form more connections with the pooler than it can support.
-   **When working in session mode (port 5432):** The max amount of clients is restricted to the "Pool Size" value in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database). If the "Pool Size" is set to 15, even if the pooler can handle 200 client connections, it will still be effectively capped at 15 for each unique ["database-role+database" combination](https://github.com/orgs/supabase/discussions/21566).
-   **When working with direct connections**: Postgres is already servicing the max amount of connections

### Solutions [#](#solutions-causes-max-client-connections-reached)

-   **Transaction Mode for serverless apps**: If you are using serverless functions (Supabase Edge, Vercel, AWS Lambda), switch to transaction mode (port 6543). It handles more connections than session mode or direct connections.
-   **Reduce the number of Prisma connections**: A single client-server can establish multiple connections with a pooler. Typically, serverless setups do not need many connections. Starting with fewer, like five or three, or even just one, is often sufficient. In serverless setups, begin with `connection_limit=1`, increasing cautiously if needed to avoid maxing out connections.
-   **Increase pool size**: If you are connecting with Supavisor, try increasing the pool size in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
-   **Disconnect appropriately**: Close Prisma connections when they are no longer needed.
-   **Decrease query time**: Reduce query complexity or add [strategic indexes](https://supabase.com/docs/guides/database/postgres/indexes) to your tables to speed up queries.
-   **Increase compute size**: Sometimes the best option is to increase your compute size, which also increases your max client size and query execution speed

* * *

## Cross schema references are only allowed when the target schema is listed in the schemas property of your data-source[#](#cross-schema-references-are-only-allowed-when-the-target-schema-is-listed-in-the-schemas-property-of-your-data-source)

A Prisma migration is referencing a schema it is not permitted to manage.

### Possible causes: [#](#possible-causes-cross-schema-references)

-   A migration references a schema that Prisma is not permitted to manage

### Solutions: [#](#solutions-cross-schema-references)

-   Multi-Schema support: If the external schema isn't Supabase managed, modify your `prisma.schema` file to enable the multi-Schema preview

```
1234567891011generator client {  provider        = "prisma-client-js"  previewFeatures = ["multiSchema"]  //Add line}datasource db {  provider  = "postgresql"  url       = env("DATABASE_URL")  directUrl = env("DIRECT_URL")  schemas   = ["public", "other_schema"] //list out relevant schemas}
```

-   Supabase managed schemas: Schemas managed by Supabase, such as `auth` and `storage`, may be changed to support new features. Referencing these schemas directly will cause schema drift in the future. It is best to remove references to these schemas from your migrations.

An alternative strategy to reference these tables is to duplicate values into Prisma managed table with triggers. Below is an example for duplicating values from `auth.users` into a table called `profiles`.

Show/Hide Details

```
12345-- Create the 'profiles' table in the 'public' schemacreate table public.profiles (  id uuid primary key,             -- 'id' is a UUID and the primary key for the table  email varchar(256)               -- 'email' is a variable character field with a maximum length of 256 characters);
```

```
123456789101112131415-- Function to handle the insertion of a new user into the 'profiles' tablecreate function public.handle_new_user()returns triggerlanguage plpgsqlsecurity definer set search_path = ''as $$begin  -- Insert the new user's data into the 'profiles' table  insert into public.profiles (id, email)  values (new.id, new.email);  return new;     -- Return the new recordend;$$;
```

```
12345678910111213141516-- Function to handle the updating of a user's information in the 'profiles' tablecreate function public.update_user()returns triggerlanguage plpgsqlsecurity definer set search_path = ''as$$begin  -- Update the user's data in the 'profiles' table  update public.profiles  set email = new.email     -- Update the 'email' field  where id = new.id;        -- Match the 'id' field with the new record  return new;  -- Return the new recordend;$$;
```

```
123456789101112131415-- Function to handle the deletion of a user from the 'profiles' tablecreate function public.delete_user()returns triggerlanguage plpgsqlsecurity definer set search_path = ''as$$begin  -- Delete the user's data from the 'profiles' table  delete from public.profiles  where id = old.id;  -- Match the 'id' field with the old record  return old;  -- Return the old recordend;$$;
```

```
1234567891011121314-- Trigger to run 'handle_new_user' function after a new user is inserted into 'auth.users' tablecreate trigger on_auth_user_created  after insert on auth.users  for each row execute procedure public.handle_new_user();-- Trigger to run 'update_user' function after a user is updated in the 'auth.users' tablecreate trigger on_auth_user_updated  after update on auth.users  for each row execute procedure public.update_user();-- Trigger to run 'delete_user' function after a user is deleted from the 'auth.users' tablecreate trigger on_auth_user_deleted  after delete on auth.users  for each row execute procedure public.delete_user();
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/prisma/prisma-troubleshooting.mdx)

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