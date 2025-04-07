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

3.  [Structured & unstructured](https://supabase.com/docs/guides/ai/structured-unstructured)

# 

Structured and Unstructured

## 

Supabase is flexible enough to associate structured and unstructured metadata with embeddings.

* * *

Most vector stores treat metadata associated with embeddings like NoSQL, unstructured data. Supabase is flexible enough to store unstructured and structured metadata.

## Structured[#](#structured)

```
1234567891011create table docs (  id uuid primary key,  embedding vector(3),  content text,  url text);insert into docs  (id, embedding, content, url)values  ('79409372-7556-4ccc-ab8f-5786a6cfa4f7', array[0.1, 0.2, 0.3], 'Hello world', '/hello-world');
```

Notice that we've associated two pieces of metadata, `content` and `url`, with the embedding. Those fields can be filtered, constrained, indexed, and generally operated on using the full power of SQL. Structured metadata fits naturally with a traditional Supabase application, and can be managed via database [migrations](https://supabase.com/docs/guides/deployment/database-migrations).

## Unstructured[#](#unstructured)

```
1234567891011121314create table docs (  id uuid primary key,  embedding vector(3),  meta jsonb);insert into docs  (id, embedding, meta)values  (    '79409372-7556-4ccc-ab8f-5786a6cfa4f7',    array[0.1, 0.2, 0.3],    '{"content": "Hello world", "url": "/hello-world"}'  );
```

An unstructured approach does not specify the metadata fields that are expected. It stores all metadata in a flexible `json`/`jsonb` column. The tradeoff is that the querying/filtering capabilities of a schemaless data type are less flexible than when each field has a dedicated column. It also pushes the burden of metadata data integrity onto application code, which is more error prone than enforcing constraints in the database.

The unstructured approach is recommended:

-   for ephemeral/interactive workloads e.g. data science or scientific research
-   when metadata fields are user-defined or unknown
-   during rapid prototyping

Client libraries like python's [vecs](https://github.com/supabase/vecs) use this structure. For example, running:

```
1234567891011121314#!/usr/bin/env python3import vecs# In practice, do not hard-code your password. Use environment variables.DB_CONNECTION = "postgresql://<user>:<password>@<host>:<port>/<db_name>"# create vector store clientvx = vecs.create_client(DB_CONNECTION)docs = vx.get_or_create_collection(name="docs", dimension=1536)docs.upsert(vectors=[  ('79409372-7556-4ccc-ab8f-5786a6cfa4f7', [100, 200, 300], { url: '/hello-world' })])
```

automatically creates the unstructured SQL table during the call to `get_or_create_collection`.

Note that when working with client libraries that emit SQL DDL, like `create table ...`, you should add that SQL to your migrations when moving to production to maintain a single source of truth for your database's schema.

## Hybrid[#](#hybrid)

The structured metadata style is recommended when the fields being tracked are known in advance. If you have a combination of known and unknown metadata fields, you can accommodate the unknown fields by adding a `json`/`jsonb` column to the table. In that situation, known fields should continue to use dedicated columns for best query performance and throughput.

```
123456789101112131415161718create table docs (  id uuid primary key,  embedding vector(3),  content text,  url string,  meta jsonb);insert into docs  (id, embedding, content, url, meta)values  (    '79409372-7556-4ccc-ab8f-5786a6cfa4f7',    array[0.1, 0.2, 0.3],    'Hello world',    '/hello-world',    '{"key": "value"}'  );
```

## Choosing the right model[#](#choosing-the-right-model)

Both approaches create a table where you can store your embeddings and some metadata. You should choose the best approach for your use-case. In summary:

-   Structured metadata is best when fields are known in advance or query patterns are predictable e.g. a production Supabase application
-   Unstructured metadata is best when fields are unknown/user-defined or when working with data interactively e.g. exploratory research

Both approaches are valid, and the one you should choose depends on your use-case.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/structured-unstructured.mdx)

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