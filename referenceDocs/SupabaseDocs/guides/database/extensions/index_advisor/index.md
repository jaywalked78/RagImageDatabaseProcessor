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

5.  [index\_advisor: Query optimization](https://supabase.com/docs/guides/database/extensions/index_advisor)

# 

index\_advisor: query optimization

* * *

[Index advisor](https://github.com/supabase/index_advisor) is a Postgres extension for recommending indexes to improve query performance.

Features:

-   Supports generic parameters e.g. `$1`, `$2`
-   Supports materialized views
-   Identifies tables/columns obfuscated by views
-   Skips duplicate indexes

`index_advisor` is accessible directly through Supabase Studio by navigating to the [Query Performance Report](https://supabase.com/dashboard/project/_/advisors/query-performance) and selecting a query and then the "indexes" tab.

![Supabase Studio index_advisor integration.](https://supabase.com/docs/img/index_advisor_studio.png)

Alternatively, you can use index\_advisor directly via SQL.

For example:

```
123456789select    *from  index_advisor('select book.id from book where title = $1'); startup_cost_before | startup_cost_after | total_cost_before | total_cost_after |                  index_statements                   | errors---------------------+--------------------+-------------------+------------------+-----------------------------------------------------+-------- 0.00                | 1.17               | 25.88             | 6.40             | {"CREATE INDEX ON public.book USING btree (title)"},| {}(1 row)
```

## Installation[#](#installation)

To get started, enable index\_advisor by running

```
1create extension index_advisor;
```

## API[#](#api)

Index advisor exposes a single function `index_advisor(query text)` that accepts a query and searches for a set of SQL DDL `create index` statements that improve the query's execution time.

The function's signature is:

```
12345678910index_advisor(query text)returns    table  (        startup_cost_before jsonb,        startup_cost_after jsonb,        total_cost_before jsonb,        total_cost_after jsonb,        index_statements text[],        errors text[]    )
```

## Usage[#](#usage)

As a minimal example, the `index_advisor` function can be given a single table query with a filter on an unindexed column.

```
12345678910111213141516create extension if not exists index_advisor cascade;create table book(  id int primary key,  title text not null);select  *from  index_advisor('select book.id from book where title = $1'); startup_cost_before | startup_cost_after | total_cost_before | total_cost_after |                  index_statements                   | errors---------------------+--------------------+-------------------+------------------+-----------------------------------------------------+-------- 0.00                | 1.17               | 25.88             | 6.40             | {"CREATE INDEX ON public.book USING btree (title)"},| {}(1 row)
```

and will return a row recommending an index on the unindexed column.

More complex queries may generate additional suggested indexes:

```
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455create extension if not exists index_advisor cascade;create table author(    id serial primary key,    name text not null);create table publisher(    id serial primary key,    name text not null,    corporate_address text);create table book(    id serial primary key,    author_id int not null references author(id),    publisher_id int not null references publisher(id),    title text);create table review(    id serial primary key,    book_id int references book(id),    body text not null);select    *from    index_advisor('        select            book.id,            book.title,            publisher.name as publisher_name,            author.name as author_name,            review.body review_body        from            book            join publisher                on book.publisher_id = publisher.id            join author                on book.author_id = author.id            join review                on book.id = review.book_id        where            author.id = $1            and publisher.id = $2    '); startup_cost_before | startup_cost_after | total_cost_before | total_cost_after |                  index_statements                         | errors---------------------+--------------------+-------------------+------------------+-----------------------------------------------------------+-------- 27.26               | 12.77              | 68.48             | 42.37            | {"CREATE INDEX ON public.book USING btree (author_id)",   | {}                                                                                    "CREATE INDEX ON public.book USING btree (publisher_id)",                                                                                    "CREATE INDEX ON public.review USING btree (book_id)"}(3 rows)
```

## Limitations[#](#limitations)

-   index\_advisor will only recommend single column, B-tree indexes. More complex indexes will be supported in future releases.
-   when a generic argument's type is not discernible from context, an error is returned in the `errors` field. To resolve those errors, add explicit type casting to the argument. e.g. `$1::int`.

## Resources[#](#resources)

-   [`index_advisor`](https://github.com/supabase/index_advisor) repo

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/index_advisor.mdx)

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