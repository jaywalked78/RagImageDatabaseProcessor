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

5.  [PGroonga: Multilingual Full Text Search](https://supabase.com/docs/guides/database/extensions/pgroonga)

# 

PGroonga: Multilingual Full Text Search

* * *

`PGroonga` is a Postgres extension adding a full text search indexing method based on [Groonga](https://groonga.org). While native Postgres supports full text indexing, it is limited to alphabet and digit based languages. `PGroonga` offers a wider range of character support making it viable for a superset of languages supported by Postgres including Japanese, Chinese, etc.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `pgroonga` and enable the extension.

## Creating a full text search index[#](#creating-a-full-text-search-index)

Given a table with a `text` column:

```
1234create table memos (  id serial primary key,  content text);
```

We can index the column for full text search with a `pgroonga` index:

```
1create index ix_memos_content ON memos USING pgroonga(content);
```

To test the full text index, we'll add some data.

```
123456insert into memos(content)values  ('PostgreSQL is a relational database management system.'),  ('Groonga is a fast full text search engine that supports all languages.'),  ('PGroonga is a PostgreSQL extension that uses Groonga as index.'),  ('There is groonga command.');
```

The Postgres query planner is smart enough to know that, for extremely small tables, it's faster to scan the whole table rather than loading an index. To force the index to be used, we can disable sequential scans:

```
12-- For testing only. Don't do this in productionset enable_seqscan = off;
```

Now if we run an explain plan on a query filtering on `memos.content`:

```
1234567explain select * from memos where content like '%engine%';                               QUERY PLAN-----------------------------------------------------------------------------Index Scan using ix_memos_content on memos  (cost=0.00..1.11 rows=1 width=36)  Index Cond: (content ~~ '%engine%'::text)(2 rows)
```

The `pgroonga` index is used to retrieve the result set:

```
123| id  | content                                                                  || --- | ------------------------------------------------------------------------ || 2   | 'Groonga is a fast full text search engine that supports all languages.' |
```

## Full text search[#](#full-text-search)

The `&@~` operator performs full text search. It returns any matching results. Unlike `LIKE` operator, `pgroonga` can search any text that contains the keyword case insensitive.

Take the following example:

```
1select * from memos where content &@~ 'groonga';
```

And the result:

```
123456id | content  ----+------------------------------------------------------------------------2 | Groonga is a fast full text search engine that supports all languages.3 | PGroonga is a PostgreSQL extension that uses Groonga as index.4 | There is groonga command.(3 rows)
```

### Match all search words[#](#match-all-search-words)

To find all memos where content contains BOTH of the words `postgres` and `pgroonga`, we can just use space to separate each words:

```
1select * from memos where content &@~ 'postgres pgroonga';
```

And the result:

```
1234id | content  ----+----------------------------------------------------------------3 | PGroonga is a PostgreSQL extension that uses Groonga as index.(1 row)
```

### Match any search words[#](#match-any-search-words)

To find all memos where content contain ANY of the words `postgres` or `pgroonga`, use the upper case `OR`:

```
1select * from memos where content &@~ 'postgres OR pgroonga';
```

And the result:

```
12345id | content  ----+----------------------------------------------------------------1 | PostgreSQL is a relational database management system.3 | PGroonga is a PostgreSQL extension that uses Groonga as index.(2 rows)
```

### Search that matches words with negation[#](#search-that-matches-words-with-negation)

To find all memos where content contain the word `postgres` but not `pgroonga`, use `-` symbol:

```
1select * from memos where content &@~ 'postgres -pgroonga';
```

And the result:

```
1234id | content  ----+--------------------------------------------------------1 | PostgreSQL is a relational database management system.(1 row)
```

## Resources[#](#resources)

-   Official [PGroonga documentation](https://pgroonga.github.io/tutorial/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pgroonga.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FMmmv9g_MiBA%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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