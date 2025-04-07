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

5.  [Vector indexes](https://supabase.com/docs/guides/ai/vector-indexes)

# 

Vector indexes

* * *

Once your vector table starts to grow, you will likely want to add an index to speed up queries. Without indexes, you'll be performing a sequential scan which can be a resource-intensive operation when you have many records.

## Choosing an index[#](#choosing-an-index)

Today `pgvector` supports two types of indexes:

-   [HNSW](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes)
-   [IVFFlat](https://supabase.com/docs/guides/ai/vector-indexes/ivf-indexes)

In general we recommend using [HNSW](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes) because of its [performance](https://supabase.com/blog/increase-performance-pgvector-hnsw#hnsw-performance-1536-dimensions) and [robustness against changing data](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes#when-should-you-create-hnsw-indexes).

## Distance operators[#](#distance-operators)

Indexes can be used to improve performance of nearest neighbor search using various distance measures. `pgvector` includes 3 distance operators:

| Operator | Description | [**Operator class**](https://www.postgresql.org/docs/current/sql-createopclass.html) |
| --- | --- | --- |
| `<->` | Euclidean distance | `vector_l2_ops` |
| `<#>` | negative inner product | `vector_ip_ops` |
| `<=>` | cosine distance | `vector_cosine_ops` |

Currently vectors with up to 2,000 dimensions can be indexed.

## Resources[#](#resources)

Read more about indexing on `pgvector`'s [GitHub page](https://github.com/pgvector/pgvector#indexing).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/vector-indexes.mdx)

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