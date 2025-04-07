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

7.  [Render](https://supabase.com/docs/guides/platform/migrating-to-supabase/render)

# 

Migrate from Render to Supabase

## 

Migrate your Render Postgres database to Supabase.

* * *

Render is a popular Web Hosting service in the online services category that also has a managed Postgres service. Render has a great developer experience, allowing users to deploy straight from GitHub or GitLab. This is the core of their product and they do it really well. However, when it comes to Postgres databases, it may not be the best option.

Supabase is one of the best free alternative to Render Postgres. Supabase provide all the backend features developers need to build a product: a Postgres database, authentication, instant APIs, edge functions, realtime subscriptions, and storage. Postgres is the core of Supabase—for example, you can use row-level security and there are more than 40 Postgres extensions available.

This guide demonstrates how to migrate from Render to Supabase to get the most out of Postgres while gaining access to all the features you need to build a project.

## Retrieve your Render database credentials [#](#retrieve-render-credentials)

1.  Log in to your [Render account](https://render.com) and select the project you want to migrate.
2.  Click **Dashboard** in the menu and click in your **Postgres** database.
3.  Scroll down in the **Info** tab.
4.  Click on **PSQL Command** and edit it adding the content after `PSQL_COMMAND=`.

![Copying PSQL command from Render dashboard](https://supabase.com/docs/img/guides/resources/migrating-to-supabase/render/render_dashboard.png) Example:

```
1%env PSQL_COMMAND=PGPASSWORD=RgaMDfTS_password_FTPa7 psql -h dpg-a_server_in.oregon-postgres.render.com -U my_db_pxl0_user my_db_pxl0
```

## Retrieve your Supabase connection string [#](#retrieve-supabase-connection-string)

1.  If you're new to Supabase, [create a project](https://supabase.com/dashboard). Make a note of your password, you will need this later. If you forget it, you can [reset it here](https://supabase.com/dashboard/project/_/settings/database).
    
2.  Go to the [Database settings](https://supabase.com/dashboard/project/_/settings/database) for your project in the Supabase Dashboard.
    
3.  Under **Connection string**, make sure `Use connection pooling` is enabled. Copy the URI and replace the password placeholder with your database password.
    

## Migrate the database[#](#migrate-the-database)

The fastest way to migrate your database is with the Supabase migration tool on [Google Colab](https://colab.research.google.com/github/mansueli/Supa-Migrate/blob/main/Migrate_Postgres_Supabase.ipynb). Alternatively, you can use the [pg\_dump](https://www.postgresql.org/docs/current/app-pgdump.html) and [psql](https://www.postgresql.org/docs/current/app-psql.html) command line tools, which are included in a full Postgres installation.

Migrate using ColabMigrate using CLI tools

1.  Set the environment variables (`PSQL_COMMAND`, `SUPABASE_HOST`, `SUPABASE_PASSWORD`) in the Colab notebook.
2.  Run the first two steps in [the notebook](https://colab.research.google.com/github/mansueli/Supa-Migrate/blob/main/Migrate_Postgres_Supabase.ipynb) in order. The first sets the variables and the second installs PSQL and the migration script.
3.  Run the third step to start the migration. This will take a few minutes.

-   If you're planning to migrate a database larger than 6 GB, we recommend [upgrading to at least a Large compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons). This will ensure you have the necessary resources to handle the migration efficiently.
    
-   For databases smaller than 150 GB, you can increase the size of the disk on paid projects by navigating to [Database Settings](https://supabase.com/dashboard/project/_/settings/database).
    
-   If you're dealing with a database larger than 150 GB, we strongly advise you to [contact our support team](https://supabase.com/dashboard/support/new) for assistance in provisioning the required resources and ensuring a smooth migration process.
    

## Enterprise[#](#enterprise)

[Contact us](https://forms.supabase.com/enterprise) if you need more help migrating your project.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/migrating-to-supabase/render.mdx)

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