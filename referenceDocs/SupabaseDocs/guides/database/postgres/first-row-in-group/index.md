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

3.  Examples

5.  [Select First Row per Group](https://supabase.com/docs/guides/database/postgres/first-row-in-group)

# 

Select first row for each group in PostgreSQL

* * *

Given a table `seasons`:

| id | team | points |
| --- | :-: | --: |
| 1 | Liverpool | 82 |
| 2 | Liverpool | 84 |
| 3 | Brighton | 34 |
| 4 | Brighton | 28 |
| 5 | Liverpool | 79 |

We want to find the rows containing the maximum number of points _per team_.

The expected output we want is:

| id | team | points |
| --- | :-: | --: |
| 3 | Brighton | 34 |
| 2 | Liverpool | 84 |

From the [SQL Editor](https://supabase.com/dashboard/project/_/sql), you can run a query like:

```
12345678910select distinct  on (team) id,  team,  pointsfrom  seasonsorder BY  id,  points desc,  team;
```

The important bits here are:

-   The `desc` keyword to order the `points` from highest to lowest.
-   The `distinct` keyword that tells Postgres to only return a single row per team.

This query can also be executed via `psql` or any other query editor if you prefer to [connect directly to the database](https://supabase.com/docs/guides/database/connecting-to-postgres#direct-connections).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/first-row-in-group.mdx)

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