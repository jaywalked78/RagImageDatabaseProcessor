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

5.  [pg\_graphql: GraphQL Support](https://supabase.com/docs/guides/database/extensions/pg_graphql)

# 

pg\_graphql: GraphQL for PostgreSQL

* * *

[pg\_graphql](https://supabase.github.io/pg_graphql/) is Postgres extension for interacting with the database using [GraphQL](https://graphql.org) instead of SQL.

The extension reflects a GraphQL schema from the existing SQL schema and exposes it through a SQL function, `graphql.resolve(...)`. This enables any programming language that can connect to Postgres to query the database via GraphQL with no additional servers, processes, or libraries.

The `pg_graphql` resolve method is designed to interop with [PostgREST](https://postgrest.org/en/stable/index.html), the tool that underpins the Supabase API, such that the `graphql.resolve` function can be called via RPC to safely and performantly expose the GraphQL API over HTTP/S.

For more information about how the SQL schema is reflected into a GraphQL schema, see the [pg\_graphql API docs](https://supabase.github.io/pg_graphql/api/).

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "pg\_graphql" and enable the extension.

## Usage[#](#usage)

Given a table

```
12345678create table "Blog"(  id serial primary key,  name text not null,  description text);insert into "Blog"(name)values ('My Blog');
```

The reflected GraphQL schema can be queried immediately as

```
12345678910111213select  graphql.resolve($$    {      blogCollection(first: 1) {        edges {          node {            id,            name          }        }      }    }  $$);
```

returning the JSON

```
1234567891011121314{  "data": {    "blogCollection": {      "edges": [        {          "node": {            "id": 1            "name": "My Blog"          }        }      ]    }  }}
```

Note that `pg_graphql` fully supports schema introspection so you can connect any GraphQL IDE or schema inspection tool to see the full set of fields and arguments available in the API.

## API[#](#api)

-   [`graphql.resolve`](https://supabase.github.io/pg_graphql/sql_interface/): A SQL function for executing GraphQL queries.

## Resources[#](#resources)

-   Official [`pg_graphql` documentation](https://github.com/supabase/pg_graphql)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_graphql.mdx)

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