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

7.  [MySQL](https://supabase.com/docs/guides/platform/migrating-to-supabase/mysql)

# 

Migrate from MySQL to Supabase

## 

Migrate your MySQL database to Supabase Postgres database.

* * *

This guide aims to exhibit the process of transferring your MySQL database to Supabase's Postgres database. Supabase is a robust and open-source platform offering a wide range of backend features, including a Postgres database, authentication, instant APIs, edge functions, real-time subscriptions, and storage. Migrating your MySQL database to Supabase's Postgres enables you to leverage PostgreSQL's capabilities and access all the features you need for your project.

## Retrieve your MySQL database credentials[#](#retrieve-your-mysql-database-credentials)

Before you begin the migration, you need to collect essential information about your MySQL database. Follow these steps:

1.  Log in to your MySQL database provider.
    
2.  Locate and note the following database details:
    
    -   Hostname or IP address
    -   Database name
    -   Username
    -   Password

## Retrieve your Supabase host [#](#retrieve-supabase-host)

1.  If you're new to Supabase, [create a project](https://supabase.com/dashboard). Make a note of your password, you will need this later. If you forget it, you can [reset it here](https://supabase.com/dashboard/project/_/settings/database).
    
2.  Go to the [Database settings](https://supabase.com/dashboard/project/_/settings/database) for your project in the Supabase Dashboard.
    
3.  Under **Connection Info**, note your Host (`$SUPABASE_HOST`).
    

![Finding Supabase host address](https://supabase.com/docs/img/guides/resources/migrating-to-supabase/mysql/database-settings-host.png)

## Migrate the database[#](#migrate-the-database)

The fastest way to migrate your database is with the Supabase migration tool on [Google Colab](https://colab.research.google.com/github/mansueli/Supa-Migrate/blob/main/Amazon_RDS_to_Supabase.ipynb).

Alternatively, you can use [pgloader](https://github.com/dimitri/pgloader), a flexible and powerful data migration tool that supports a wide range of source database engines, including MySQL and MS SQL, and migrates the data to a Postgres database. For databases using the Postgres engine, we recommend using the [`pg_dump`](https://www.postgresql.org/docs/current/app-pgdump.html) and [psql](https://www.postgresql.org/docs/current/app-psql.html) command line tools, which are included in a full Postgres installation.

Migrate using ColabMigrate from MySQL with pgloader

1.  Select the Database Engine from the Source database in the dropdown
2.  Set the environment variables (`HOST`, `USER`, `SOURCE_DB`,`PASSWORD`, `SUPABASE_URL`, and `SUPABASE_PASSWORD`) in the Colab notebook.
3.  Run the first two steps in [the notebook](https://colab.research.google.com/github/mansueli/Supa-Migrate/blob/main/Amazon_RDS_to_Supabase.ipynb) in order. The first sets engine and installs the necessary files.
4.  Run the third step to start the migration. This will take a few minutes.

-   If you're planning to migrate a database larger than 6 GB, we recommend [upgrading to at least a Large compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons). This will ensure you have the necessary resources to handle the migration efficiently.
    
-   For databases smaller than 150 GB, you can increase the size of the disk on paid projects by navigating to [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
    
-   If you're dealing with a database larger than 150 GB, we strongly advise you to [contact our support team](https://supabase.com/dashboard/support/new) for assistance in provisioning the required resources and ensuring a smooth migration process.
    

## Enterprise[#](#enterprise)

[Contact us](https://forms.supabase.com/enterprise) if you need more help migrating your project.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/migrating-to-supabase/mysql.mdx)

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