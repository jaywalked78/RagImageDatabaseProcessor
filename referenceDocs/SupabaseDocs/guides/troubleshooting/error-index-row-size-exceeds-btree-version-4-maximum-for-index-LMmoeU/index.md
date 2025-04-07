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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Error: index row size exceeds btree version 4 maximum for index

Last edited: 2/4/2025

* * *

## Error[#](#error)

```
1index row size exceeds btree version 4 maximum 2704 for index "idx_name"
```

## Summary[#](#summary)

PG has a limit on a B-tree tuple(=row) size. It needs to fit at least 3 B-tree tuples on a 8Kb page. That could not be changed.

B-tree row can be a single attribute or multiple attributes. These cases are better addressed separately.

## B-tree is built with multiple attributes[#](#b-tree-is-built-with-multiple-attributes)

B-tree with multiple attributes will perform better than several only in case the likely SELECT queries use several attributes that include the first attributes that are in the index. I.e. select by 1-st, 2-nd, 3-d but not by 2-nd, 3-d and 5-th index attributes.

The other case when multiple attributes B-tree is good is when we have INSERT/UPDATE workload that is comparable to SELECT load (generally SELECTS a way more often). Then we can save speed-up updating a single index instead of several at INSERT/UPDATE at cost of SELECT performance decrease.

But most likely we have multiple attributes B-tree index due to some automation tool, not by intention. Even without the mentioned error it's best to build separate single-attribute indexes for each attribute from it. Then drop multiple attributes B-tree index. This is a must and the only solution when we have this error though.

## B-tree is built on a single attribute that is very long[#](#b-tree-is-built-on-a-single-attribute-that-is-very-long)

This can be if the index is built on text, JSON column etc. It's not prohibited to build B-tree on these datatypes, but it's also ineffective. Why?

One of the measures of index efficiency is the ratio of index entries to the width of all possible values space for this datatype. If we have say 100000 distinct values of int32 in the index then the ratio is 1/40000. If we have text with length of 2704 bytes (maximum for B-tree index) we can hardly imagine the number of distinct values that gives us even a comparable ratio. That said indexing of that long values stores much redundancy in the index.

The solution is simple: use some king of hashing to transfer the values to much narrower space. I.e. md5. The solution is simple, you build a functional index (=index by expression):

```
1CREATE INDEX ON table_name(MD5(column_name));
```

instead of:

```
1CREATE INDEX ON table_name(column_name);
```

Then you must modify you SELECTs to be using the same function (otherwise the functional index will not be used in SELECT queries). I.e.

```
1select * from table_name where MD5(column_name) = MD5('search_value');
```

instead of

```
1select * from table_name where column_name = 'search_value';
```

[More on building index by expression](https://www.postgresql.org/docs/current/sql-createindex.html)

For some datatypes other than text that allows queries by partial inclusion (i.e. that the pair key-value is includes in a JSON or for implementing tsvector phrase search) you'd just use GIST/GIN indexes that inherently have values space much narrower that the whole to be indexed.

[More on GIN/GiST indexes](https://www.postgresql.org/docs/15/textsearch-indexes.html)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[btree](https://supabase.com/docs/guides/troubleshooting?tags=btree)[index](https://supabase.com/docs/guides/troubleshooting?tags=index)[attribute](https://supabase.com/docs/guides/troubleshooting?tags=attribute)[size](https://supabase.com/docs/guides/troubleshooting?tags=size)[hashing](https://supabase.com/docs/guides/troubleshooting?tags=hashing)

* * *

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