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

5.  [Metabase](https://supabase.com/docs/guides/database/metabase)

# 

Connecting to Metabase

* * *

[`Metabase`](https://www.metabase.com/) is an Open Source data visualization tool. You can use it to explore your data stored in Supabase.

1

### Register

Create a [Metabase account](https://store.metabase.com/checkout) or deploy locally with [Docker](https://www.docker.com/products/docker-desktop/)

Deploying with Docker:

```
1docker pull metabase/metabase:latest
```

Then run:

```
1docker run -d -p 3000:3000 --name metabase metabase/metabase
```

The server should be available at [`http://localhost:3000/setup`](http://localhost:3000/setup)

2

### Connect to Postgres

Connect your Postgres server to Metabase.

-   On your project dashboard click on [Connect](https://supabase.com/dashboard/project/_?showConnect=true)
-   View parameters under "Session pooler"

##### connection notice

If you're in an [IPv6 environment](https://supabase.com/docs/guides/platform/ipv4-address#checking-your-network-ipv6-support) or have the [IPv4 Add-On](https://supabase.com/docs/guides/platform/ipv4-address#understanding-ip-addresses), you can use the direct connection string instead of Supavisor in Session mode.

-   Enter your database credentials into Metabase

Example credentials: ![Name Postgres Server.](https://supabase.com/docs/img/guides/database/connecting-to-postgres/metabase/add-pg-server.png)

3

### Explore

Explore your data in Metabase

![explore data](https://supabase.com/docs/img/guides/database/connecting-to-postgres/metabase/explore.png)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/metabase.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)