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

AI & Vectors

1.  [AI & Vectors](https://supabase.com/docs/guides/ai)

3.  Python Client

5.  [Choosing a Client](https://supabase.com/docs/guides/ai/python-clients)

# 

Choosing a Client

* * *

As described in [Structured & Unstructured Embeddings](https://supabase.com/docs/guides/ai/structured-unstructured), AI workloads come in many forms.

For data science or ephemeral workloads, the [Supabase Vecs](https://supabase.github.io/vecs/) client gets you started quickly. All you need is a connection string and vecs handles setting up your database to store and query vectors with associated metadata.

You can get your connection string from the [**Database Settings**](https://supabase.com/dashboard/project/_/settings/database) page in your dashboard. Make sure to check **Use connection pooling**, then copy the URI. Also, change the URI scheme from `postgres` to `postgresql`. `vecs` uses SQLAlchemy under the hood, which only supports `postgresql` as a dialect.

For production python applications with version controlled migrations, we recommend adding first class vector support to your toolchain by [registering the vector type with your ORM](https://github.com/pgvector/pgvector-python). pgvector provides bindings for the most commonly used SQL drivers/libraries including Django, SQLAlchemy, SQLModel, psycopg, asyncpg and Peewee.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/python-clients.mdx)

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