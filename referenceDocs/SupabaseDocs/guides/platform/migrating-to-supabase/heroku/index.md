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

7.  [Heroku](https://supabase.com/docs/guides/platform/migrating-to-supabase/heroku)

# 

Migrate from Heroku to Supabase

## 

Migrate your Heroku Postgres database to Supabase.

* * *

Supabase is one of the best [free alternatives to Heroku Postgres](https://supabase.com/alternatives/supabase-vs-heroku-postgres). This guide shows how to migrate your Heroku Postgres database to Supabase. This migration requires the [pg\_dump](https://www.postgresql.org/docs/current/app-pgdump.html) and [psql](https://www.postgresql.org/docs/current/app-psql.html) CLI tools, which are installed automatically as part of the complete Postgres installation package.

Alternatively, use the [Heroku to Supabase migration tool](https://migrate.supabase.com/) to migrate in just a few clicks.

## Quick demo[#](#quick-demo)

## Retrieve your Heroku database credentials [#](#retrieve-heroku-credentials)

1.  Log in to your [Heroku account](https://heroku.com) and select the project you want to migrate.
2.  Click **Resources** in the menu and select your **Heroku Postgres** database.
3.  Click **Settings** in the menu.
4.  Click **View Credentials** and save the following information:
    -   Host (`$HEROKU_HOST`)
    -   Database (`$HEROKU_DATABASE`)
    -   User (`$HEROKU_USER`)
    -   Password (`$HEROKU_PASSWORD`)

## Retrieve your Supabase connection string [#](#retrieve-supabase-connection-string)

1.  If you're new to Supabase, [create a project](https://supabase.com/dashboard).
2.  Go to the [Database settings](https://supabase.com/dashboard/project/_/settings/database) for your project in the Supabase Dashboard.
3.  Under **Connection string**, make sure `Use connection pooling` is enabled. Copy the URI and replace the password placeholder with your database password.

## Export your Heroku database to a file [#](#export-heroku-database)

Use `pg_dump` with your Heroku credentials to export your Heroku database to a file (e.g., `heroku_dump.sql`).

```
123pg_dump --clean --if-exists --quote-all-identifiers \ -h $HEROKU_HOST -U $HEROKU_USER -d $HEROKU_DATABASE \ --no-owner --no-privileges > heroku_dump.sql
```

## Import the database to your Supabase project [#](#import-database-to-supabase)

Use `psql` to import the Heroku database file to your Supabase project.

```
1psql -d "$YOUR_CONNECTION_STRING" -f heroku_dump.sql
```

## Additional options[#](#additional-options)

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

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/migrating-to-supabase/heroku.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FxsRhPMphtZ4%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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