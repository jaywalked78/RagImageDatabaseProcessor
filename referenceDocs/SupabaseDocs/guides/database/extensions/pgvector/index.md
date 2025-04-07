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

3.  Extensions

5.  [pgvector: Embeddings and vector similarity](https://supabase.com/docs/guides/database/extensions/pgvector)

# 

pgvector: Embeddings and vector similarity

* * *

[pgvector](https://github.com/pgvector/pgvector/) is a Postgres extension for vector similarity search. It can also be used for storing [embeddings](https://supabase.com/blog/openai-embeddings-postgres-vector).

The name of pgvector's Postgres extension is [vector](https://github.com/pgvector/pgvector/blob/258eaf58fdaff1843617ff59ea855e0768243fe9/README.md?plain=1#L64).

Learn more about Supabase's [AI & Vector](https://supabase.com/docs/guides/ai) offering.

## Concepts[#](#concepts)

### Vector similarity[#](#vector-similarity)

Vector similarity refers to a measure of the similarity between two related items. For example, if you have a list of products, you can use vector similarity to find similar products. To do this, you need to convert each product into a "vector" of numbers, using a mathematical model. You can use a similar model for text, images, and other types of data. Once all of these vectors are stored in the database, you can use vector similarity to find similar items.

### Embeddings[#](#embeddings)

This is particularly useful if you're building on top of OpenAI's [GPT-3](https://openai.com/blog/gpt-3-apps/). You can create and store [embeddings](https://supabase.com/docs/guides/ai/quickstarts/generate-text-embeddings) for retrieval augmented generation.

## Usage[#](#usage)

### Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "vector" and enable the extension.

## Usage[#](#usage)

### Create a table to store vectors[#](#create-a-table-to-store-vectors)

```
123456create table posts (  id serial primary key,  title text not null,  body text not null,  embedding vector(384));
```

### Storing a vector / embedding[#](#storing-a-vector--embedding)

In this example we'll generate a vector using Transformer.js, then store it in the database using the Supabase client.

```
123456789101112131415161718192021import { pipeline } from '@xenova/transformers'const generateEmbedding = await pipeline('feature-extraction', 'Supabase/gte-small')const title = 'First post!'const body = 'Hello world!'// Generate a vector using Transformers.jsconst output = await generateEmbedding(body, {  pooling: 'mean',  normalize: true,})// Extract the embedding outputconst embedding = Array.from(output.data)// Store the vector in Postgresconst { data, error } = await supabase.from('posts').insert({  title,  body,  embedding,})
```

## Specific usage cases[#](#specific-usage-cases)

### Queries with filtering[#](#queries-with-filtering)

If you use an IVFFlat or HNSW index and naively filter the results based on the value of another column, you may get fewer rows returned than requested.

For example, the following query may return fewer than 5 rows, even if 5 corresponding rows exist in the database. This is because the embedding index may not return 5 rows matching the filter.

```
1SELECT * FROM items WHERE category_id = 123 ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

To get the exact number of requested rows, use [iterative search](https://github.com/pgvector/pgvector/?tab=readme-ov-file#iterative-index-scans) to continue scanning the index until enough results are found.

## More pgvector and Supabase resources[#](#more-pgvector-and-supabase-resources)

-   [Supabase Clippy: ChatGPT for Supabase Docs](https://supabase.com/blog/chatgpt-supabase-docs)
-   [Storing OpenAI embeddings in Postgres with pgvector](https://supabase.com/blog/openai-embeddings-postgres-vector)
-   [A ChatGPT Plugins Template built with Supabase Edge Runtime](https://supabase.com/blog/building-chatgpt-plugins-template)
-   [Template for building your own custom ChatGPT style doc search](https://github.com/supabase-community/nextjs-openai-doc-search)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pgvector.mdx)

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