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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  More

5.  [Migrating to Supabase](https://supabase.com/docs/guides/platform/migrating-to-supabase)

7.  [Vercel Postgres](https://supabase.com/docs/guides/platform/migrating-to-supabase/vercel-postgres)

# 

Migrate from Vercel Postgres to Supabase

## 

Migrate your existing Vercel Postgres database to Supabase.

* * *

This guide demonstrates how to migrate your Vercel Postgres database to Supabase to get the most out of Postgres while gaining access to all the features you need to build a project.

## Retrieve your Vercel Postgres database credentials [#](#retrieve-credentials)

1.  Log in to your Vercel Dashboard [https://vercel.com/login](https://vercel.com/login).
2.  Click on the **Storage** tab.
3.  Click on your Postgres Database.
4.  Under the **Quickstart** section, select **psql** then click **Show Secret** to reveal your database password.
5.  Copy the string after `psql` to the clipboard.

Example:

```
1psql "postgres://default:xxxxxxxxxxxx@yy-yyyyy-yyyyyy-yyyyyyy.us-west-2.aws.neon.tech:5432/verceldb?sslmode=require"
```

Copy this part to your clipboard:

```
1"postgres://default:xxxxxxxxxxxx@yy-yyyyy-yyyyyy-yyyyyyy.us-west-2.aws.neon.tech:5432/verceldb?sslmode=require"
```

## Set your `OLD_DB_URL` environment variable[#](#set-your-olddburl-environment-variable)

Set the **OLD\_DB\_URL** environment variable at the command line using your Vercel Postgres Database credentials.

Example:

```
1export OLD_DB_URL="postgres://default:xxxxxxxxxxxx@yy-yyyyy-yyyyyy-yyyyyyy.us-west-2.aws.neon.tech:5432/verceldb?sslmode=require"
```

## Retrieve your Supabase connection string [#](#retrieve-supabase-connection-string)

1.  If you're new to Supabase, [create a project](https://supabase.com/dashboard). Make a note of your password, you will need this later. If you forget it, you can [reset it here](https://supabase.com/dashboard/project/_/settings/database).
    
2.  Go to the [Database settings](https://supabase.com/dashboard/project/_/settings/database) for your project in the Supabase Dashboard.
    
3.  Under **Connection string**, select **URI**, make sure **Display connection pooler** is checked, and **Mode: Session** is set.
    
4.  Click the **Copy** button to the right of your connection string to copy it to the clipboard.
    

## Set your `NEW_DB_URL` environment variable[#](#set-your-newdburl-environment-variable)

Set the **NEW\_DB\_URL** environment variable at the command line using your Supabase connection string. You will need to replace `[YOUR-PASSWORD]` with your actual database password.

Example:

```
1export NEW_DB_URL="postgresql://postgres.xxxxxxxxxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
```

## Migrate the database[#](#migrate-the-database)

You will need the [pg\_dump](https://www.postgresql.org/docs/current/app-pgdump.html) and [psql](https://www.postgresql.org/docs/current/app-psql.html) command line tools, which are included in a full [Postgres installation](https://www.postgresql.org/download).

1.  Export your database to a file in console
    
    Use `pg_dump` with your Postgres credentials to export your database to a file (e.g., `dump.sql`).
    

```
1234567pg_dump "$OLD_DB_URL" \  --clean \  --if-exists \  --quote-all-identifiers \  --no-owner \  --no-privileges \  > dump.sql
```

2.  Import the database to your Supabase project
    
    Use `psql` to import the Postgres database file to your Supabase project.
    
    ```
    1psql -d "$NEW_DB_URL" -f dump.sql
    ```
    

Additional options

-   To only migrate a single database schema, add the `--schema=PATTERN` parameter to your `pg_dump` command.
-   To exclude a schema: `--exclude-schema=PATTERN`.
-   To only migrate a single table: `--table=PATTERN`.
-   To exclude a table: `--exclude-table=PATTERN`.

Run `pg_dump --help` for a full list of options.

-   If you're planning to migrate a database larger than 6 GB, we recommend [upgrading to at least a Large compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons). This will ensure you have the necessary resources to handle the migration efficiently.
    
-   For databases smaller than 150 GB, you can increase the size of the disk on paid projects by navigating to [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
    
-   If you're dealing with a database larger than 150 GB, we strongly advise you to [contact our support team](https://supabase.com/dashboard/support/new) for assistance in provisioning the required resources and ensuring a smooth migration process.
    

## Enterprise[#](#enterprise)

[Contact us](https://forms.supabase.com/enterprise) if you need more help migrating your project.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/migrating-to-supabase/vercel-postgres.mdx)

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