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

3.  Python Examples

5.  [Developing locally with Vecs](https://supabase.com/docs/guides/ai/vecs-python-client)

# 

Python client

## 

Manage unstructured vector stores in PostgreSQL.

* * *

Supabase provides a Python client called [`vecs`](https://github.com/supabase/vecs) for managing unstructured vector stores. This client provides a set of useful tools for creating and querying collections in Postgres using the [pgvector](https://supabase.com/docs/guides/database/extensions/pgvector) extension.

## Quick start[#](#quick-start)

Let's see how Vecs works using a local database. Make sure you have the Supabase CLI [installed](https://supabase.com/docs/guides/cli#installation) on your machine.

### Initialize your project[#](#initialize-your-project)

Start a local Postgres instance in any folder using the `init` and `start` commands. Make sure you have Docker running!

```
12345# Initialize your projectsupabase init# Start Postgressupabase start
```

### Create a collection[#](#create-a-collection)

Inside a Python shell, run the following commands to create a new collection called "docs", with 3 dimensions.

```
1234567import vecs# create vector store clientvx = vecs.create_client("postgresql://postgres:postgres@localhost:54322/postgres")# create a collection of vectors with 3 dimensionsdocs = vx.get_or_create_collection(name="docs", dimension=3)
```

### Add embeddings[#](#add-embeddings)

Now we can insert some embeddings into our "docs" collection using the `upsert()` command:

```
12345678910111213import vecs# create vector store clientdocs = vecs.get_or_create_collection(name="docs", dimension=3)# a collection of vectors with 3 dimensionsvectors=[  ("vec0", [0.1, 0.2, 0.3], {"year": 1973}),  ("vec1", [0.7, 0.8, 0.9], {"year": 2012})]# insert our vectorsdocs.upsert(vectors=vectors)
```

### Query the collection[#](#query-the-collection)

You can now query the collection to retrieve a relevant match:

```
12345678910import vecsdocs = vecs.get_or_create_collection(name="docs", dimension=3)# query the collection filtering metadata for "year" = 2012docs.query(    data=[0.4,0.5,0.6],      # required    limit=1,                         # number of records to return    filters={"year": {"$eq": 2012}}, # metadata filters)
```

## Deep dive[#](#deep-dive)

For a more in-depth guide on `vecs` collections, see [API](https://supabase.com/docs/guides/ai/python/api).

## Resources[#](#resources)

-   Official Vecs Documentation: [https://supabase.github.io/vecs/api](https://supabase.github.io/vecs/api)
-   Source Code: [https://github.com/supabase/vecs](https://github.com/supabase/vecs)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/vecs-python-client.mdx)

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