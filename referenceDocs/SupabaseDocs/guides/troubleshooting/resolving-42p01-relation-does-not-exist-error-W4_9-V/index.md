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

# Resolving 42P01: relation does not exist error

Last edited: 1/16/2025

* * *

`42P01` is a [Postgres level error](https://www.postgresql.org/docs/current/errcodes-appendix.html), that can also be found in the [PostgREST error docs](https://postgrest.org/en/v12/references/errors.html)

```
142P01: relation "<some table name>" does not exist
```

## There are a few possible causes[#](#there-are-a-few-possible-causes)

* * *

### Cause 1: Search path broken[#](#cause-1-search-path-broken)

When directly accessing a table that is not in the `public` schema, it's important to reference the external schema explicitly in your query. Below is an example from the [JS client:](https://supabase.com/docs/reference/javascript/select)

```
1const { data, error } = await supabase.schema('myschema').from('mytable').select()
```

If after calling the table directly, you get a `42501` permission denied error, then you must also [expose the custom schema to the API.](https://supabase.com/docs/guides/api/using-custom-schemas). For Supabase managed schemas, such as `vault` and `auth`, these cannot be directly accessed through the DB REST API for security reasons. If necessary, they can be strictly accessed through [security definer functions.](https://supabase.com/docs/guides/database/functions?queryGroups=language&language=sql&queryGroups=example-view&example-view=sql#security-definer-vs-invoker)

* * *

### Cause 2: Ignoring capitalization and other typos[#](#cause-2-ignoring-capitalization-and-other-typos)

The table could be defined as: CREATE TABLE “Hello”\`. The double quotes make it case-sensitive, so it becomes essential to call the table with the appropriate title. It is possible to change the table name to be lowercase for convenience, either in the Table Editor, or with raw SQL:

```
12alter table "Table_name"rename to table_name;
```

* * *

### Cause 3: Table or function actually does not exist[#](#cause-3-table-or-function-actually-does-not-exist)

One may have never made the table or dropped it deliberately or accidentally. This can be quickly checked with the following query:

```
123-- For tablesSELECT * FROM information_schema.tablesWHERE table_name ILIKE 'example_table'; --<------ Add relevant table name
```

```
12345678910-- For functionsselect  p.proname as function_name,  n.nspname as schema_name,  pg_get_functiondef(p.oid) as function_definitionfrom  pg_proc as p  join pg_namespace as n on p.pronamespace = n.oidwhere n.nspname in ('public', 'your custom schema') -- <------ Add other relevant schemasorder by n.nspname, p.proname;
```

* * *

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[42P01](https://supabase.com/docs/guides/troubleshooting?errorCodes=42P01)[42501](https://supabase.com/docs/guides/troubleshooting?errorCodes=42501)

* * *

### Tags

[relation](https://supabase.com/docs/guides/troubleshooting?tags=relation)[schema](https://supabase.com/docs/guides/troubleshooting?tags=schema)[capitalization](https://supabase.com/docs/guides/troubleshooting?tags=capitalization)

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