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

# Prisma Error Management

Last edited: 2/21/2025

* * *

> This guide has been deprecated. Use the troubleshooting guide in the [Supabase docs](https://supabase.com/docs/guides/database/prisma/prisma-troubleshooting).

# Addressing specific errors:

Prisma, unlike other libraries, uses [query parameters for configurations](https://www.prisma.io/docs/orm/overview/databases/postgresql#arguments).

Some can be used to address specific errors and can be appended to end of your connection string like so:

```
1.../postgres?KEY1=VALUE&KEY2=VALUE&KEY3=VALUE
```

## `Can't reach database server at`:[#](#cant-reach-database-server-at-)

Increase `connect_timeout` to 30s and check to make sure you are using a valid connection string.

```
1.../postgres?connect_timeout=30
```

## `Timed out fetching a new connection from the connection pool`:[#](#timed-out-fetching-a-new-connection-from-the-connection-pool-)

Increase `pool_timeout` to 30s .

```
1.../postgres?pool_timeout=30
```

## `... prepared statement "" already exists`[#](#-prepared-statement--already-exists)

Add pgbouncer=true to the connection string.

```
1.../postgres?pgbouncer=true
```

## `Max client connections reached`[#](#max-client-connections-reached)

Checkout this [guide](https://github.com/orgs/supabase/discussions/22305) for managing this error

## `Server has closed the connection`[#](#server-has-closed-the-connection)

According to this [GitHub Issue for Prisma](https://github.com/prisma/prisma/discussions/7389), it may be related to large return values for queries. Try to limit the total amount of rows returned for particularly large requests.

## `Drift detected: Your database schema is not in sync with your migration history`[#](#drift-detected-your-database-schema-is-not-in-sync-with-your-migration-history)

Prisma will try to act as the source of truth for your database structures. If you `CREATE`, `DROP`, or `ALTER` database objects outside of a Prisma Migration, it is likely to detect drift and may offer to correct the situation by purging your schemas. To circumvent this issue, try [baselining your migrations](https://www.prisma.io/docs/orm/prisma-migrate/workflows/baselining).

Some users have discussed how they managed this problem in a [GitHub Discussion.](https://github.com/prisma/prisma/issues/19100#top)

# Management suggestions

## Make a custom role for Prisma to increase observability[#](#make-a-custom-role-for-prisma-to-increase-observability)

**Imagine your database as a house, and users as the people with keys.**

-   By default, most developers use the "master key" (the `postgres` role) to access everything. But it's safer to give Prisma its own key! This way, it can only access the rooms (tables) it needs.
-   it's usually safer to give Prisma its own key! This way, it can only access the rooms (tables) it needs.
-   Plus, with separate keys, it's easier to see what Prisma is doing in your house with monitoring tools, such as [PGAudit](https://supabase.com/docs/guides/database/extensions/pgaudit?queryGroups=database-method&database-method=sql) and [pg\_stat\_activity](https://supabase.com/docs/guides/platform/performance).

### Creating the Prisma user:[#](#creating-the-prisma-user)

```
1create user "prisma" with password 'secret_password' bypassrls createdb;
```

> Prisma requires the [`createdb` modifier](https://supabase.com/blog/postgres-roles-and-privileges#role-attributes) to create shadow databases. It uses them to help manage migrations.

### Give Postgres ownership of the new user:[#](#give-postgres-ownership-of-the-new-user)

This allows you to view Prisma migration changes in the [Dashboard](https://supabase.com/dashboard/project/_/editor)

```
1grant "prisma" to "postgres";
```

### Keep it safe![#](#keep-it-safe)

Use a strong password for Prisma. Bitwarden provides a free and simple [password generator](https://bitwarden.com/password-generator/) that can make one for you.

If you need to change it later, you can use the below SQL:

```
1alter user "prisma" with password 'new_password';
```

### Grant Prisma access[#](#grant-prisma-access)

The below example gives Prisma full authority over all database objects in the public schema:

```
123456789-- Grant it necessary permissions over the relevant schemas (public)  grant usage on schema public to prisma;  grant create on schema public to prisma;  grant all on all tables in schema public to prisma;  grant all on all routines in schema public to prisma;  grant all on all sequences in schema public to prisma;  alter default privileges for role postgres in schema public grant all on tables to prisma;  alter default privileges for role postgres in schema public grant all on routines to prisma;  alter default privileges for role postgres in schema public grant all on sequences to prisma;
```

> For more guidance on specifying access, check out this [article](https://supabase.com/blog/postgres-roles-and-privileges#creating-objects-and-assigning-privileges) on privileges

## Optimize Prisma queries:[#](#optimize-prisma-queries)

In the [Query Performance Advisor](https://supabase.com/dashboard/project/_/database/query-performance), you can view long-running or frequently accessed queries by role:

![Screenshot 2024-06-19 at 1 25 16 PM](https://github.com/supabase/supabase/assets/91111415/46e2feae-9fca-4436-a957-2c995eb5ca92)

Selecting a query can reveal suggestions to improve its performance

## Configuring connections[#](#configuring-connections)

Useful Links:

-   [How to Monitor Connections and Find the Correct Pool Size](https://github.com/orgs/supabase/discussions/27141).
-   [Supavisor FAQ](https://github.com/orgs/supabase/discussions/21566)

Supabase provides 3 connection strings in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database). You can use all three or just the ones most relevant to your project.

### Direct connection:[#](#direct-connection)

Best used with stationary servers, such as VMs and long-standing containers, but it only works in IPv6 environments unless the [IPv4 Add-On](https://supabase.com/dashboard/project/_/settings/addons) is enabled. If you are unsure if your network is IPv6 compatible, [check here](https://github.com/orgs/supabase/discussions/27034).

```
123# Example Connectionpostgresql://postgres:[PASSWORD]@db.[PROJECT REF].supabase.co:5432/postgres
```

### Supavisor in session mode (port 5432):[#](#supavisor-in-session-mode-port-5432)

```
123# Example Connectionpostgres://[DB-USER].[PROJECT REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```

An alternative to direct connections when working in IPv4-only environments.

> Session mode is a good option for migrations

### Supavisor in transaction mode (port 6543):[#](#supavisor-in-transaction-mode-port-6543)

```
123# Example Connectionpostgres://[DB-USER].[PROJECT REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Should be used when deploying to:

-   Horizontally auto-scaling servers
-   Edge/Serverless deployments

When working in serverless/edge environments, it is recommended to set the `connection_limit=1` and then gradually increase it if necessary.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[prisma](https://supabase.com/docs/guides/troubleshooting?tags=prisma)[timeout](https://supabase.com/docs/guides/troubleshooting?tags=timeout)[connection](https://supabase.com/docs/guides/troubleshooting?tags=connection)[pgbouncer](https://supabase.com/docs/guides/troubleshooting?tags=pgbouncer)[schema](https://supabase.com/docs/guides/troubleshooting?tags=schema)[migration](https://supabase.com/docs/guides/troubleshooting?tags=migration)

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