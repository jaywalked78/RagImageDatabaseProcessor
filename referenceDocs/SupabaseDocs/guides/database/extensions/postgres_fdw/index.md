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

5.  [postgres\_fdw: query data from an external Postgres server](https://supabase.com/docs/guides/database/extensions/postgres_fdw)

# 

postgres\_fdw

* * *

The extension enables Postgres to query tables and views on a remote Postgres server.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "postgres\_fdw" and enable the extension.

## Create a connection to another database[#](#create-a-connection-to-another-database)

1

### Create a foreign server

Define the remote database address

```
1234567create server "<foreign_server_name>"    foreign data wrapper postgres_fdw    options (        host '<host>',        port '<port>',        dbname '<dbname>'    );
```

2

### Create a server mapping

Set the user credentials for the remote server

```
123456create user mapping for "<dbname>"server "<foreign_server_name>"options (    user '<db_user>',    password '<password>');
```

3

### Import tables

Import tables from the foreign database

Example: Import all tables from a schema

```
123import foreign schema "<foreign_schema>"from server "<foreign_server>"into "<host_schema>";
```

Example: Import specific tables

```
1234567import foreign schema "<foreign_schema>"limit to (    "<table_name1>",    "<table_name2>")from server "<foreign_server>"into "<host_schema>";
```

4

### Query foreign table

```
1select * from "<foreign_table>"
```

### Configuring execution options[#](#configuring-execution-options)

#### Fetch\_size[#](#fetchsize)

Maximum rows fetched per operation. For example, fetching 200 rows with `fetch_size` set to 100 requires 2 requests.

```
12alter server "<foreign_server_name>"options (fetch_size '10000');
```

#### Batch\_size[#](#batchsize)

Maximum rows inserted per cycle. For example, inserting 200 rows with `batch_size` set to 100 requires 2 requests.

```
12alter server "<foreign_server_name>"options (batch_size '1000');
```

#### Extensions[#](#extensions)

Lists shared extensions. Without them, queries involving unlisted extension functions or operators may fail or omit references.

```
12alter server "<foreign_server_name>"options (extensions 'vector, postgis');
```

For more server options, check the extension's [official documentation](https://www.postgresql.org/docs/current/postgres-fdw.html#POSTGRES-FDW)

## Resources[#](#resources)

-   Official [`postgres_fdw` documentation](https://www.postgresql.org/docs/current/postgres-fdw.html#POSTGRES-FDW)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/postgres_fdw.mdx)

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