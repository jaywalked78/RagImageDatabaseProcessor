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

3.  OrioleDB

5.  [Overview](https://supabase.com/docs/guides/database/orioledb)

# 

OrioleDB Overview

* * *

The [OrioleDB](https://www.orioledb.com/) Postgres extension provides a drop-in replacement storage engine for the default heap storage method. It is designed to improve Postgres' scalability and performance.

OrioleDB addresses PostgreSQL's scalability limitations by removing bottlenecks in the shared memory cache under high concurrency. It also optimizes write-ahead-log (WAL) insertion through row-level WAL logging. These changes lead to significant improvements in the industry standard TPC-C benchmark, which approximates a real-world transactional workload. The following benchmark was performed on a c7g.metal instance and shows OrioleDB's performance outperforming the default Postgres heap method with a 3.3x speedup.

OrioleDB is in active development and currently has [certain limitations](https://www.orioledb.com/docs/usage/getting-started#current-limitations). Currently, only B-tree indexes are supported, so features like pg\_vector's HNSW indexes are not yet available. An Index Access Method bridge to unlock support for all index types used with heap storage is under active development. In the Supabase OrioleDB image the default storage method has been updated to use OrioleDB, granting better performance out of the box.

## Concepts[#](#concepts)

### Index-organized tables[#](#index-organized-tables)

OrioleDB uses index-organized tables, where table data is stored in the index structure. This design eliminates the need for separate heap storage, reduces overhead and improves lookup performance for primary key queries.

### No buffer mapping[#](#no-buffer-mapping)

In-memory pages are connected to the storage pages using direct links. This allows OrioleDB to bypass PostgreSQL's shared buffer pool and eliminate the associated complexity and contention in buffer mapping.

### Undo log[#](#undo-log)

Multi-Version Concurrency Control (MVCC) is implemented using an undo log. The undo log stores previous row versions and transaction information, which enables consistent reads while removing the need for table vacuuming completely.

### Copy-on-write checkpoints[#](#copy-on-write-checkpoints)

OrioleDB implements copy-on-write checkpoints to persist data efficiently. This approach writes only modified data during a checkpoint, reducing the I/O overhead compared to traditional Postgres checkpointing and allowing row-level WAL logging.

## Usage[#](#usage)

### Creating OrioleDB project[#](#creating-orioledb-project)

You can get started with OrioleDB by enabling the extension in your Supabase dashboard. To get started with OrioleDB you need to [create a new Supabase project](https://supabase.com/dashboard/new/_) and choose `OrioleDB Public Alpha` Postgres version.

### Creating tables[#](#creating-tables)

To create a table using the OrioleDB storage engine just execute the standard `CREATE TABLE` statement. By default it will create a table using OrioleDB storage engine. For example:

```
12345678910-- Create a tablecreate table blog_post (  id int8 not null,  title text not null,  body text not null,  author text not null,  published_at timestamptz not null default CURRENT_TIMESTAMP,  views bigint not null,  primary key (id));
```

### Creating indexes[#](#creating-indexes)

OrioleDB tables always have a primary key. If it wasn't defined explicitly, a hidden primary key is created using the `ctid` column. Additionally you can create secondary indexes.

Currently, only B-tree indexes are supported, so features like pg\_vector's HNSW indexes are not yet available.

```
1234-- Create an indexcreate index blog_post_published_at on blog_post (published_at);create index blog_post_views on blog_post (views) where (views > 1000);
```

### Data manipulation[#](#data-manipulation)

You can query and modify data in OrioleDB tables using standard SQL statements, including `SELECT`, `INSERT`, `UPDATE`, `DELETE` and `INSERT ... ON CONFLICT`.

```
1234567INSERT INTO blog_post (id, title, body, author, views)VALUES (1, 'Hello, World!', 'This is my first blog post.', 'John Doe', 1000);SELECT * FROM blog_post ORDER BY published_at DESC LIMIT 10; id │     title     │            body             │  author  │         published_at          │ views────┼───────────────┼─────────────────────────────┼──────────┼───────────────────────────────┼───────  1 │ Hello, World! │ This is my first blog post. │ John Doe │ 2024-11-15 12:04:18.756824+01 │  1000
```

### Viewing query plans[#](#viewing-query-plans)

You can see the execution plan using standard `EXPLAIN` statement.

```
12345678910111213141516171819EXPLAIN SELECT * FROM blog_post ORDER BY published_at DESC LIMIT 10;                                                 QUERY PLAN──────────────────────────────────────────────────────────────────────────────────────────────────────────── Limit  (cost=0.15..1.67 rows=10 width=120)   ->  Index Scan Backward using blog_post_published_at on blog_post  (cost=0.15..48.95 rows=320 width=120)EXPLAIN SELECT * FROM blog_post WHERE id = 1;                                    QUERY PLAN────────────────────────────────────────────────────────────────────────────────── Index Scan using blog_post_pkey on blog_post  (cost=0.15..8.17 rows=1 width=120)   Index Cond: (id = 1)EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM blog_post ORDER BY published_at DESC LIMIT 10;                                                                      QUERY PLAN────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Limit  (cost=0.15..1.67 rows=10 width=120) (actual time=0.052..0.054 rows=1 loops=1)   ->  Index Scan Backward using blog_post_published_at on blog_post  (cost=0.15..48.95 rows=320 width=120) (actual time=0.050..0.052 rows=1 loops=1) Planning Time: 0.186 ms Execution Time: 0.088 ms
```

## Resources[#](#resources)

-   [Official OrioleDB documentation](https://www.orioledb.com/docs)
-   [OrioleDB GitHub repository](https://github.com/orioledb/orioledb)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/orioledb.mdx)

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