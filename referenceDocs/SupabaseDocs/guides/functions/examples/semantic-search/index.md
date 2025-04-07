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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Examples

5.  [Semantic AI Search](https://supabase.com/docs/guides/functions/examples/semantic-search)

# 

Semantic Search

## 

Semantic Search with pgvector and Supabase Edge Functions

* * *

[Semantic search](https://supabase.com/docs/guides/ai/semantic-search) interprets the meaning behind user queries rather than exact [keywords](https://supabase.com/docs/guides/ai/keyword-search). It uses machine learning to capture the intent and context behind the query, handling language nuances like synonyms, phrasing variations, and word relationships.

Since Supabase Edge Runtime [v1.36.0](https://github.com/supabase/edge-runtime/releases/tag/v1.36.0) you can run the [`gte-small` model](https://huggingface.co/Supabase/gte-small) natively within Supabase Edge Functions without any external dependencies! This allows you to generate text embeddings without calling any external APIs!

In this tutorial you're implementing three parts:

1.  A [`generate-embedding`](https://github.com/supabase/supabase/tree/master/examples/ai/edge-functions/supabase/functions/generate-embedding/index.ts) database webhook edge function which generates embeddings when a content row is added (or updated) in the [`public.embeddings`](https://github.com/supabase/supabase/tree/master/examples/ai/edge-functions/supabase/migrations/20240408072601_embeddings.sql) table.
2.  A [`query_embeddings` Postgres function](https://github.com/supabase/supabase/tree/master/examples/ai/edge-functions/supabase/migrations/20240410031515_vector-search.sql) which allows us to perform similarity search from an Edge Function via [Remote Procedure Call (RPC)](https://supabase.com/docs/guides/database/functions?language=js).
3.  A [`search` edge function](https://github.com/supabase/supabase/tree/master/examples/ai/edge-functions/supabase/functions/search/index.ts) which generates the embedding for the search term, performs the similarity search via RPC function call, and returns the result.

You can find the complete example code on [GitHub](https://github.com/supabase/supabase/tree/master/examples/ai/edge-functions)

### Create the database table and webhook[#](#create-the-database-table-and-webhook)

Given the [following table definition](https://github.com/supabase/supabase/blob/master/examples/ai/edge-functions/supabase/migrations/20240408072601_embeddings.sql):

```
12345678910create extension if not exists vector with schema extensions;create table embeddings (  id bigint primary key generated always as identity,  content text not null,  embedding vector (384));alter table embeddings enable row level security;create index on embeddings using hnsw (embedding vector_ip_ops);
```

You can deploy the [following edge function](https://github.com/supabase/supabase/blob/master/examples/ai/edge-functions/supabase/functions/generate-embedding/index.ts) as a [database webhook](https://supabase.com/docs/guides/database/webhooks) to generate the embeddings for any text content inserted into the table:

```
123456789101112131415161718192021const model = new Supabase.ai.Session('gte-small')Deno.serve(async (req) => {  const payload: WebhookPayload = await req.json()  const { content, id } = payload.record  // Generate embedding.  const embedding = await model.run(content, {    mean_pool: true,    normalize: true,  })  // Store in database.  const { error } = await supabase    .from('embeddings')    .update({ embedding: JSON.stringify(embedding) })    .eq('id', id)  if (error) console.warn(error.message)  return new Response('ok')})
```

## Create a Database Function and RPC[#](#create-a-database-function-and-rpc)

With the embeddings now stored in your Postgres database table, you can query them from Supabase Edge Functions by utilizing [Remote Procedure Calls (RPC)](https://supabase.com/docs/guides/database/functions?language=js).

Given the [following Postgres Function](https://github.com/supabase/supabase/blob/master/examples/ai/edge-functions/supabase/migrations/20240410031515_vector-search.sql):

```
123456789101112131415161718192021222324-- Matches document sections using vector similarity search on embeddings---- Returns a setof embeddings so that we can use PostgREST resource embeddings (joins with other tables)-- Additional filtering like limits can be chained to this function callcreate or replace function query_embeddings(embedding vector(384), match_threshold float)returns setof embeddingslanguage plpgsqlas $$begin  return query  select *  from embeddings  -- The inner product is negative, so we negate match_threshold  where embeddings.embedding <#> embedding < -match_threshold  -- Our embeddings are normalized to length 1, so cosine similarity  -- and inner product will produce the same query results.  -- Using inner product which can be computed faster.  --  -- For the different distance functions, see https://github.com/pgvector/pgvector  order by embeddings.embedding <#> embedding;end;$$;
```

## Query vectors in Supabase Edge Functions[#](#query-vectors-in-supabase-edge-functions)

You can use `supabase-js` to first generate the embedding for the search term and then invoke the Postgres function to find the relevant results from your stored embeddings, right from your [Supabase Edge Function](https://github.com/supabase/supabase/blob/master/examples/ai/edge-functions/supabase/functions/search/index.ts):

```
12345678910111213141516171819202122232425const model = new Supabase.ai.Session('gte-small')Deno.serve(async (req) => {  const { search } = await req.json()  if (!search) return new Response('Please provide a search param!')  // Generate embedding for search term.  const embedding = await model.run(search, {    mean_pool: true,    normalize: true,  })  // Query embeddings.  const { data: result, error } = await supabase    .rpc('query_embeddings', {      embedding,      match_threshold: 0.8,    })    .select('content')    .limit(3)  if (error) {    return Response.json(error)  }  return Response.json({ search, result })})
```

You now have AI powered semantic search set up without any external dependencies! Just you, pgvector, and Supabase Edge Functions!

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/semantic-search.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2Fw4Rr_1whU-U%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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