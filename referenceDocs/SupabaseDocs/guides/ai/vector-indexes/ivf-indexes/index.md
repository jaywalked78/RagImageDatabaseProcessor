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

3.  More

5.  [Vector indexes](https://supabase.com/docs/guides/ai/vector-indexes)

7.  [IVFFlat indexes](https://supabase.com/docs/guides/ai/vector-indexes/ivf-indexes)

# 

IVFFlat indexes

* * *

IVFFlat is a type of vector index for approximate nearest neighbor search. It is a frequently used index type that can improve performance when querying highly-dimensional vectors, like those representing embeddings.

## Choosing an index[#](#choosing-an-index)

Today `pgvector` supports two types of indexes:

-   [HNSW](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes)
-   [IVFFlat](https://supabase.com/docs/guides/ai/vector-indexes/ivf-indexes)

In general we recommend using [HNSW](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes) because of its [performance](https://supabase.com/blog/increase-performance-pgvector-hnsw#hnsw-performance-1536-dimensions) and [robustness against changing data](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes#when-should-you-create-hnsw-indexes). If you have a special use case that requires IVFFlat instead, keep reading.

## Usage[#](#usage)

The way you create an IVFFlat index depends on the distance operator you are using. `pgvector` includes 3 distance operators:

| Operator | Description | [**Operator class**](https://www.postgresql.org/docs/current/sql-createopclass.html) |
| --- | --- | --- |
| `<->` | Euclidean distance | `vector_l2_ops` |
| `<#>` | negative inner product | `vector_ip_ops` |
| `<=>` | cosine distance | `vector_cosine_ops` |

Use the following SQL commands to create an IVFFlat index for the operator(s) used in your queries.

### Euclidean L2 distance (`vector_l2_ops`)[#](#euclidean-l2-distance--vectorl2ops-)

```
1create index on items using ivfflat (column_name vector_l2_ops) with (lists = 100);
```

### Inner product (`vector_ip_ops`)[#](#inner-product--vectoripops-)

```
1create index on items using ivfflat (column_name vector_ip_ops) with (lists = 100);
```

### Cosine distance (`vector_cosine_ops`)[#](#cosine-distance--vectorcosineops-)

```
1create index on items using ivfflat (column_name vector_cosine_ops) with (lists = 100);
```

Currently vectors with up to 2,000 dimensions can be indexed.

## How does IVFFlat work?[#](#how-does-ivfflat-work)

IVF stands for 'inverted file indexes'. It works by clustering your vectors in order to reduce the similarity search scope. Rather than comparing a vector to every other vector, the vector is only compared against vectors within the same cell cluster (or nearby clusters, depending on your configuration).

### Inverted lists (cell clusters)[#](#inverted-lists-cell-clusters)

When you create the index, you choose the number of inverted lists (cell clusters). Increase this number to speed up queries, but at the expense of recall.

For example, to create an index with 100 lists on a column that uses the cosine operator:

```
1create index on items using ivfflat (column_name vector_cosine_ops) with (lists = 100);
```

For more info on the different operators, see [Distance operations](#distance-operators).

For every query, you can set the number of probes (1 by default). The number of probes corresponds to the number of nearby cells to probe for a match. Increase this for better recall at the expense of speed.

To set the number of probes for the duration of the session run:

```
1set ivfflat.probes = 10;
```

To set the number of probes only for the current transaction run:

```
1234begin;set local ivfflat.probes = 10;select ...commit;
```

If the number of probes is the same as the number of lists, exact nearest neighbor search will be performed and the planner won't use the index.

### Approximate nearest neighbor[#](#approximate-nearest-neighbor)

One important note with IVF indexes is that nearest neighbor search is approximate, since exact search on high dimensional data can't be indexed efficiently. This means that similarity results will change (slightly) after you add an index (trading recall for speed).

## When should you create IVFFlat indexes?[#](#when-should-you-create-ivfflat-indexes)

`pgvector` recommends building IVFFlat indexes only after the table has sufficient data, so that the internal IVFFlat cell clusters are based on your data's distribution. Anytime the distribution changes significantly, consider rebuilding indexes.

## Resources[#](#resources)

Read more about indexing on `pgvector`'s [GitHub page](https://github.com/pgvector/pgvector#indexing).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/vector-indexes/ivf-indexes.mdx)

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