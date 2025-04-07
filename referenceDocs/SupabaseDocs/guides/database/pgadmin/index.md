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

3.  GUI quickstarts

5.  [pgAdmin](https://supabase.com/docs/guides/database/pgadmin)

# 

Connecting with pgAdmin

* * *

[`pgAdmin`](https://www.pgadmin.org/) is a GUI tool for managing Postgres databases. You can use it to connect to your database via SSL.

1

### Register

Register a new Postgres server.

2

### Name

Name your server.

![Name Postgres Server.](https://supabase.com/docs/img/guides/database/connecting-to-postgres/pgadmin/name-pg-server.png)

3

### Connect

Add the connection info. Go to your [`Database Settings`](https://supabase.com/dashboard/project/_/settings/database). Make sure `Use connection pooling` is enabled. Switch the connection mode to `Session` and copy your connection parameters. Fill in your Database password that you made when creating your project (It can be reset in Database Settings above if you don't have it).

![Add Connection Info.](https://supabase.com/docs/img/guides/database/connecting-to-postgres/pgadmin/add-pg-server-conn-info.png)

4

### SSL

Download your SSL certificate from Dashboard's [`Database Settings`](https://supabase.com/dashboard/project/_/settings/database).

In pgAdmin, navigate to the Parameters tab and select connection parameter as Root Certificate. Next navigate to the Root certificate input, it will open up a file-picker modal. Select the certificate you downloaded earlier and save the server details. pgAdmin should now be able to connect to your Postgres via SSL.

![Add Connection Info.](https://supabase.com/docs/img/guides/database/connecting-to-postgres/pgadmin/database-settings-host.png)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/pgadmin.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)