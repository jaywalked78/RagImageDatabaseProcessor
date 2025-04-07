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

3.  Debugging

5.  [Timeouts](https://supabase.com/docs/guides/database/postgres/timeouts)

# 

Timeouts

## 

Extend database timeouts to execute longer transactions

* * *

Dashboard and [Client](https://supabase.com/docs/guides/api/rest/client-libs) queries have a max-configurable timeout of 60 seconds. For longer transactions, use [Supavisor or direct connections](https://supabase.com/docs/guides/database/connecting-to-postgres#quick-summary).

## Change Postgres timeout[#](#change-postgres-timeout)

You can change the Postgres timeout at the:

1.  [Session level](#session-level)
2.  [Function level](#function-level)
3.  [Global level](#global-level)
4.  [Role level](#role-level)

### Session level[#](#session-level)

Session level settings persist only for the duration of the connection.

Set the session timeout by running:

```
1set statement_timeout = '10min';
```

Because it applies to sessions only, it can only be used with connections through Supavisor in session mode (port 5432) or a direct connection. It cannot be used in the Dashboard, with the Supabase Client API, nor with Supavisor in Transaction mode (port 6543).

This is most often used for single, long running, administrative tasks, such as creating an HSNW index. Once the setting is implemented, you can view it by executing:

```
1SHOW statement_timeout;
```

See the full guide on [changing session timeouts](https://github.com/orgs/supabase/discussions/21133).

### Function level[#](#function-level)

This works with the Database REST API when called from the Supabase client libraries:

```
123456create or replace function myfunc()returns void as $$ select pg_sleep(3); -- simulating some long-running process$$language sqlset statement_timeout TO '4s'; -- set custom timeout
```

This is mostly for recurring functions that need a special exemption for runtimes.

### Role level[#](#role-level)

This sets the timeout for a specific role.

The default role timeouts are:

-   `anon`: 3s
-   `authenticated`: 8s
-   `service_role`: none (defaults to the `authenticator` role's 8s timeout if unset)
-   `postgres`: none (capped by default global timeout to be 2min)

Run the following query to change a role's timeout:

```
1alter role example_role set statement_timeout = '10min'; -- could also use seconds '10s'
```

If you are changing the timeout for the Supabase Client API calls, you will need to reload PostgREST to reflect the timeout changes by running the following script:

```
1NOTIFY pgrst, 'reload config';
```

Unlike global settings, the result cannot be checked with `SHOW statement_timeout`. Instead, run:

```
123456789101112select  rolname,  rolconfigfrom pg_roleswhere  rolname in (    'anon',    'authenticated',    'postgres',    'service_role'    -- ,<ANY CUSTOM ROLES>  );
```

### Global level[#](#global-level)

This changes the statement timeout for all roles and sessions without an explicit timeout already set.

```
1alter database postgres set statement_timeout TO '4s';
```

Check if your changes took effect:

```
1show statement_timeout;
```

Although not necessary, if you are uncertain if a timeout has been applied, you can run a quick test:

```
12345create or replace function myfunc()returns void as $$  select pg_sleep(601); -- simulating some long-running process$$language sql;
```

## Identifying timeouts[#](#identifying-timeouts)

The Supabase Dashboard contains tools to help you identify timed-out and long-running queries.

### Using the Logs Explorer[#](#using-the-logs-explorer)

Go to the [Logs Explorer](https://supabase.com/dashboard/project/_/logs/explorer), and run the following query to identify timed-out events (`statement timeout`) and queries that successfully run for longer than 10 seconds (`duration`).

```
1234567891011121314151617181920select  cast(postgres_logs.timestamp as datetime) as timestamp,  event_message,  parsed.error_severity,  parsed.user_name,  parsed.query,  parsed.detail,  parsed.hint,  parsed.sql_state_code,  parsed.backend_typefrom  postgres_logs  cross join unnest(metadata) as metadata  cross join unnest(metadata.parsed) as parsedwhere  regexp_contains(event_message, 'duration|statement timeout')  -- (OPTIONAL) MODIFY OR REMOVE  and parsed.user_name = 'authenticator' -- <--------CHANGEorder by timestamp desclimit 100;
```

### Using the Query Performance page[#](#using-the-query-performance-page)

Go to the [Query Performance page](https://supabase.com/dashboard/project/_/advisors/query-performance?preset=slowest_execution) and filter by relevant role and query speeds. This only identifies slow-running but successful queries. Unlike the Log Explorer, it does not show you timed-out queries.

### Understanding roles in logs[#](#understanding-roles-in-logs)

Each API server uses a designated user for connecting to the database:

| Role | API/Tool |
| --- | --- |
| `supabase_admin` | Used by Realtime and for project configuration |
| `authenticator` | PostgREST |
| `supabase_auth_admin` | Auth |
| `supabase_storage_admin` | Storage |
| `supabase_replication_admin` | Synchronizes Read Replicas |
| `postgres` | Supabase Dashboard and External Tools (e.g., Prisma, SQLAlchemy, PSQL...) |
| Custom roles | External Tools (e.g., Prisma, SQLAlchemy, PSQL...) |

Filter by the `parsed.user_name` field to only retrieve logs made by specific users:

```
12345-- find events based on role/server... querywhere  -- find events from the relevant role  parsed.user_name = '<ROLE>'
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/timeouts.mdx)

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