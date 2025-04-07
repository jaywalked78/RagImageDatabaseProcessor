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

5.  [PSQL](https://supabase.com/docs/guides/database/psql)

# 

Connecting with PSQL

* * *

[`psql`](https://www.postgresql.org/docs/current/app-psql.html) is a command-line tool that comes with Postgres.

## Connecting with SSL[#](#connecting-with-ssl)

You should connect to your database using SSL wherever possible, to prevent snooping and man-in-the-middle attacks.

You can obtain your connection info and Server root certificate from your application's dashboard:

![Connection Info and Certificate.](https://supabase.com/docs/img/database/database-settings-ssl.png)

Download your [SSL certificate](#connecting-with-ssl) to `/path/to/prod-supabase.cer`.

Find your connection settings. Go to your [`Database Settings`](https://supabase.com/dashboard/project/_/settings/database) and make sure `Use connection pooling` is checked. Change the connection mode to `Session`, and copy the parameters into the connection string:

```
1psql "sslmode=verify-full sslrootcert=/path/to/prod-supabase.cer host=[CLOUD_PROVIDER]-0-[REGION].pooler.supabase.com dbname=postgres user=postgres.[PROJECT_REF]"
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/psql.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)