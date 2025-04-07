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

5.  [pg\_hashids: Short UIDs](https://supabase.com/docs/guides/database/extensions/pg_hashids)

# 

pg\_hashids: Short UIDs

* * *

[pg\_hashids](https://github.com/iCyberon/pg_hashids) provides a secure way to generate short, unique, non-sequential ids from numbers. The hashes are intended to be small, easy-to-remember identifiers that can be used to obfuscate data (optionally) with a password, alphabet, and salt. For example, you may wish to hide data like user IDs, order numbers, or tracking codes in favor of `pg_hashid`'s unique identifiers.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "pg\_hashids" and enable the extension.

## Usage[#](#usage)

Suppose we have a table that stores order information, and we want to give customers a unique identifier without exposing the sequential `id` column. To do this, we can use `pg_hashid`'s `id_encode` function.

```
123456789101112131415161718192021create table orders (  id serial primary key,  description text,  price_cents bigint);insert into orders (description, price_cents)values ('a book', 9095);select  id,  id_encode(id) as short_id,  description,  price_centsfrom  orders;  id | short_id | description | price_cents----+----------+-------------+-------------  1 | jR       | a book      |        9095(1 row)
```

To reverse the `short_id` back into an `id`, there is an equivalent function named `id_decode`.

## Resources[#](#resources)

-   Official [pg\_hashids documentation](https://github.com/iCyberon/pg_hashids)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_hashids.mdx)

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