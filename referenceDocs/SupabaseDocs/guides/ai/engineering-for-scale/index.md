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

3.  Learn

5.  [Engineering for scale](https://supabase.com/docs/guides/ai/engineering-for-scale)

# 

Engineering for Scale

## 

Building an enterprise-grade vector architecture.

* * *

Content sources for vectors can be extremely large. As you grow you should run your Vector workloads across several secondary databases (sometimes called "pods"), which allows each collection to scale independently.

## Simple workloads[#](#simple-workloads)

For small workloads, it's typical to store your data in a single database.

If you've used [Vecs](https://supabase.com/docs/guides/ai/vecs-python-client) to create 3 different collections, you can expose collections to your web or mobile application using [views](https://supabase.com/docs/guides/database/tables#views):

For example, with 3 collections, called `docs`, `posts`, and `images`, we could expose the "docs" inside the public schema like this:

```
1234567create view public.docs asselect  id,  embedding,  metadata, # Expose the metadata as JSON  (metadata->>'url')::text as url # Extract the URL as a stringfrom vector
```

You can then use any of the client libraries to access your collections within your applications:

```
1234const { data, error } = await supabase  .from('docs')  .select('id, embedding, metadata')  .eq('url', '/hello-world')
```

## Enterprise workloads[#](#enterprise-workloads)

As you move into production, we recommend splitting your collections into separate projects. This is because it allows your vector stores to scale independently of your production data. Vectors typically grow faster than operational data, and they have different resource requirements. Running them on separate databases removes the single-point-of-failure.

You can use as many secondary databases as you need to manage your collections. With this architecture, you have 2 options for accessing collections within your application:

1.  Query the collections directly using Vecs.
2.  Access the collections from your Primary database through a Wrapper.

You can use both of these in tandem to suit your use-case. We recommend option `1` wherever possible, as it offers the most scalability.

### Query collections using Vecs[#](#query-collections-using-vecs)

Vecs provides methods for querying collections, either using a [cosine similarity function](https://supabase.github.io/vecs/api/#basic) or with [metadata filtering](https://supabase.github.io/vecs/api/#metadata-filtering).

```
123456789# cosine similaritydocs.query(query_vector=[0.4,0.5,0.6], limit=5)# metadata filteringdocs.query(    query_vector=[0.4,0.5,0.6],    limit=5,    filters={"year": {"$eq": 2012}}, # metadata filters)
```

### Accessing external collections using Wrappers[#](#accessing-external-collections-using-wrappers)

Supabase supports [Foreign Data Wrappers](https://supabase.com/blog/postgres-foreign-data-wrappers-rust). Wrappers allow you to connect two databases together so that you can query them over the network.

This involves 2 steps: connecting to your remote database from the primary and creating a Foreign Table.

#### Connecting your remote database[#](#connecting-your-remote-database)

Inside your Primary database we need to provide the credentials to access the secondary database:

```
123456789create extension postgres_fdw;create server docs_serverforeign data wrapper postgres_fdwoptions (host 'db.xxx.supabase.co', port '5432', dbname 'postgres');create user mapping for docs_userserver docs_serveroptions (user 'postgres', password 'password');
```

#### Create a foreign table[#](#create-a-foreign-table)

We can now create a foreign table to access the data in our secondary project.

```
12345678create foreign table docs (  id text not null,  embedding vector(384),  metadata jsonb,  url text)server docs_serveroptions (schema_name 'public', table_name 'docs');
```

This looks very similar to our View example above, and you can continue to use the client libraries to access your collections through the foreign table:

```
1234const { data, error } = await supabase  .from('docs')  .select('id, embedding, metadata')  .eq('url', '/hello-world')
```

### Enterprise architecture[#](#enterprise-architecture)

This diagram provides an example architecture that allows you to access the collections either with our client libraries or using Vecs. You can add as many secondary databases as you need (in this example we only show one):

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/engineering-for-scale.mdx)

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