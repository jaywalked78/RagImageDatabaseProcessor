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

5.  [pg\_jsonschema: JSON Schema Validation](https://supabase.com/docs/guides/database/extensions/pg_jsonschema)

# 

pg\_jsonschema: JSON Schema Validation

* * *

[JSON Schema](https://json-schema.org) is a language for annotating and validating JSON documents. [`pg_jsonschema`](https://github.com/supabase/pg_jsonschema) is a Postgres extension that adds the ability to validate PostgreSQL's built-in `json` and `jsonb` data types against JSON Schema documents.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `pg_jsonschema` and enable the extension.

## Functions[#](#functions)

-   [`json_matches_schema(schema json, instance json)`](https://github.com/supabase/pg_jsonschema#api): Checks if a `json` _instance_ conforms to a JSON Schema _schema_.
-   [`jsonb_matches_schema(schema json, instance jsonb)`](https://github.com/supabase/pg_jsonschema#api): Checks if a `jsonb` _instance_ conforms to a JSON Schema _schema_.

## Usage[#](#usage)

Since `pg_jsonschema` exposes its utilities as functions, we can execute them with a select statement:

```
12345select  extensions.json_matches_schema(    schema := '{"type": "object"}',    instance := '{}'  );
```

`pg_jsonschema` is generally used in tandem with a [check constraint](https://www.postgresql.org/docs/current/ddl-constraints.html) as a way to constrain the contents of a json/b column to match a JSON Schema.

```
123456789101112131415161718192021222324252627282930313233343536create table customer(    id serial primary key,    ...    metadata json,    check (        json_matches_schema(            '{                "type": "object",                "properties": {                    "tags": {                        "type": "array",                        "items": {                            "type": "string",                            "maxLength": 16                        }                    }                }            }',            metadata        )    ));-- Example: Valid Payloadinsert into customer(metadata)values ('{"tags": ["vip", "darkmode-ui"]}');-- Result:--   INSERT 0 1-- Example: Invalid Payloadinsert into customer(metadata)values ('{"tags": [1, 3]}');-- Result:--   ERROR:  new row for relation "customer" violates check constraint "customer_metadata_check"--   DETAIL:  Failing row contains (2, {"tags": [1, 3]}).
```

## Resources[#](#resources)

-   Official [`pg_jsonschema` documentation](https://github.com/supabase/pg_jsonschema)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_jsonschema.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FamJo48ChLGs%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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