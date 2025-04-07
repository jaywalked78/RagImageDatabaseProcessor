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

REST API

1.  [REST API](https://supabase.com/docs/guides/api)

3.  [Using the Data APIs](https://supabase.com/docs/guides/api/data-apis)

5.  [Converting from SQL to JavaScript API](https://supabase.com/docs/guides/api/sql-to-api)

# 

Converting SQL to JavaScript API

* * *

Many common SQL queries can be written using the JavaScript API, provided by the SDK to wrap Data API calls. Below are a few examples of conversions between SQL and JavaScript patterns.

## Select statement with basic clauses[#](#select-statement-with-basic-clauses)

Select a set of columns from a single table with where, order by, and limit clauses.

```
12345select first_name, last_name, team_id, agefrom playerswhere age between 20 and 24 and team_id != 'STL'order by last_name, first_name desclimit 20;
```

```
123456789const { data, error } = await supabase  .from('players')  .select('first_name,last_name,team_id,age')  .gte('age', 20)  .lte('age', 24)  .not('team_id', 'eq', 'STL')  .order('last_name', { ascending: true }) // or just .order('last_name')  .order('first_name', { ascending: false })  .limit(20)
```

## Select statement with complex Boolean logic clause[#](#select-statement-with-complex-boolean-logic-clause)

Select all columns from a single table with a complex where clause: OR AND OR

```
123select *from playerswhere ((team_id = 'CHN' or team_id is null) and (age > 35 or age is null));
```

```
12345const { data, error } = await supabase  .from('players')  .select() // or .select('*')  .or('team_id.eq.CHN,team_id.is.null')  .or('age.gt.35,age.is.null') // additional filters imply "AND"
```

Select all columns from a single table with a complex where clause: AND OR AND

```
123select *from playerswhere ((team_id = 'CHN' and age > 35) or (team_id != 'CHN' and age is not null));
```

```
1234const { data, error } = await supabase  .from('players')  .select() // or .select('*')  .or('and(team_id.eq.CHN,age.gt.35),and(team_id.neq.CHN,.not.age.is.null)')
```

## Resources[#](#resources)

-   [Supabase - Get started for free](https://supabase.com)
-   [PostgREST Operators](https://postgrest.org/en/stable/api.html#operators)
-   [Supabase API: JavaScript select](https://supabase.com/docs/reference/javascript/select)
-   [Supabase API: JavaScript modifiers](https://supabase.com/docs/reference/javascript/using-modifiers)
-   [Supabase API: JavaScript filters](https://supabase.com/docs/reference/javascript/using-filters)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/api/sql-to-api.mdx)

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