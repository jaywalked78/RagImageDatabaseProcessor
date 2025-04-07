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

3.  Fundamentals

5.  [Securing your data](https://supabase.com/docs/guides/database/secure-data)

# 

Securing your data

* * *

Supabase helps you control access to your data. With access policies, you can protect sensitive data and make sure users only access what they're allowed to see.

## Connecting your app securely[#](#connecting-your-app-securely)

Supabase allows you to access your database using the auto-generated [Data APIs](https://supabase.com/docs/guides/database/connecting-to-postgres#data-apis). This speeds up the process of building web apps, since you don't need to write your own backend services to pass database queries and results back and forth.

You can keep your data secure while accessing the Data APIs from the frontend, so long as you:

-   Turn on [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) (RLS) for your tables
-   Use your Supabase **anon key** when you create a Supabase client

Your anon key is safe to expose with RLS enabled, because row access permission is checked against your access policies and the user's [JSON Web Token (JWT)](https://supabase.com/docs/learn/auth-deep-dive/auth-deep-dive-jwts). The JWT is automatically sent by the Supabase client libraries if the user is logged in using Supabase Auth.

##### Never expose your service role key on the frontend

Unlike your anon key, your **service role key** is **never** safe to expose because it bypasses RLS. Only use your service role key on the backend. Treat it as a secret (for example, import it as a sensitive environment variable instead of hardcoding it).

## More information[#](#more-information)

Supabase and Postgres provide you with multiple ways to manage security, including but not limited to Row Level Security. See the Access and Security pages for more information:

-   [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
-   [Column Level Security](https://supabase.com/docs/guides/database/postgres/column-level-security)
-   [Hardening the Data API](https://supabase.com/docs/guides/database/hardening-data-api)
-   [Managing Postgres roles](https://supabase.com/docs/guides/database/postgres/roles)
-   [Managing secrets with Vault](https://supabase.com/docs/guides/database/vault)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/secure-data.mdx)

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