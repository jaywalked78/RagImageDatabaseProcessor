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

3.  Fundamentals

5.  [Connecting to your database](https://supabase.com/docs/guides/database/connecting-to-postgres)

# 

Connect to your database

## 

Connect to Postgres from your frontend, backend, or serverless environment

* * *

## Quick summary[#](#quick-summary)

How you connect to your database depends on where you're connecting from:

-   For frontend applications, use the [Data API](#data-apis-and-client-libraries)
-   For Postgres clients, use a connection string
    -   For single sessions (for example, database GUIs) or Postgres native commands (for example, using client applications like [pg\_dump](https://www.postgresql.org/docs/current/app-pgdump.html) or specifying connections for [replication](https://supabase.com/docs/guides/database/postgres/setup-replication-external)) use the [direct connection string](#direct-connection) if your environment supports IPv6
    -   For persistent clients, and support for both IPv4 and IPv6, use [Supavisor session mode](#supavisor-session-mode)
    -   For temporary clients (for example, serverless or edge functions) use [Supavisor transaction mode](#supavisor-transaction-mode)

## Quickstarts[#](#quickstarts)

[

Prisma







](https://supabase.com/docs/guides/database/prisma)[

Drizzle







](https://supabase.com/docs/guides/database/drizzle)[

Postgres.js







](https://supabase.com/docs/guides/database/postgres-js)[

pgAdmin







](https://supabase.com/docs/guides/database/pgadmin)[

PSQL







](https://supabase.com/docs/guides/database/psql)[

DBeaver







](https://supabase.com/docs/guides/database/dbeaver)[

Metabase







](https://supabase.com/docs/guides/database/metabase)[

Beekeeper Studio







](https://supabase.com/docs/guides/database/beekeeper-studio)

## Data APIs and client libraries[#](#data-apis-and-client-libraries)

The Data APIs allow you to interact with your database using REST or GraphQL requests. You can use these APIs to fetch and insert data from the frontend, as long as you have [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) enabled.

-   [REST](https://supabase.com/docs/guides/api)
-   [GraphQL](https://supabase.com/docs/guides/graphql/api)

For convenience, you can also use the Supabase client libraries, which wrap the Data APIs with a developer-friendly interface and automatically handle authentication:

-   [JavaScript](https://supabase.com/docs/reference/javascript)
-   [Flutter](https://supabase.com/docs/reference/dart)
-   [Swift](https://supabase.com/docs/reference/swift)
-   [Python](https://supabase.com/docs/reference/python)
-   [C#](https://supabase.com/docs/reference/csharp)
-   [Kotlin](https://supabase.com/docs/reference/kotlin)

## Direct connection[#](#direct-connection)

The direct connection string connects directly to your Postgres instance. It is ideal for persistent servers, such as virtual machines (VMs) and long-lasting containers. Examples include AWS EC2 machines, Fly.io VMs, and DigitalOcean Droplets.

Direct connections use IPv6 by default. If your environment doesn't support IPv6, use [Supavisor session mode](#supavisor-session-mode) or get the [IPv4 add-on](https://supabase.com/docs/guides/platform/ipv4-address).

The connection string looks like this:

```
1postgresql://postgres:[YOUR-PASSWORD]@db.apbkobhfnmcqqzqeeqss.supabase.co:5432/postgres
```

Get your project's direct string from the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) page:

1.  Go to the `Settings` section.
2.  Click `Database`.
3.  Under `Connection string`, make sure `Display connection pooler` is unchecked. Copy the URI.

## Shared pooler[#](#shared-pooler)

Every Supabase project includes a free, shared connection pooler. This is ideal for persistent servers when IPv6 is not supported.

### Supavisor session mode[#](#supavisor-session-mode)

The session mode connection string connects to your Postgres instance via a proxy.

The connection string looks like this:

```
1postgres://postgres.apbkobhfnmcqqzqeeqss:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
```

Get your project's session mode string from the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) page:

1.  Go to the `Settings` section.
2.  Click `Database`.
3.  Under `Connection string`, make sure `Display connection pooler` is checked and `Session mode` is selected. Copy the URI.

### Supavisor transaction mode[#](#supavisor-transaction-mode)

The transaction mode connection string connects to your Postgres instance via a proxy which serves as a connection pooler. This is ideal for serverless or edge functions, which require many transient connections.

Transaction mode does not support [prepared statements](https://postgresql.org/docs/current/sql-prepare.html). To avoid errors, [turn off prepared statements](https://github.com/orgs/supabase/discussions/28239) for your connection library.

The connection string looks like this:

```
1postgres://postgres.apbkobhfnmcqqzqeeqss:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Get your project's transaction mode string from the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) page:

1.  Go to the `Settings` section.
2.  Click `Database`.
3.  Under `Connection string`, make sure `Display connection pooler` is checked and `Transaction mode` is selected. Copy the URI.

## Dedicated pooler[#](#dedicated-pooler)

For paying customers, we provision a Dedicated Pooler ([PgBouncer](https://www.pgbouncer.org/)) that's co-located with your Postgres database. This will require you to connect with IPv6 or, if that's not an option, you can use the [IPv4 add-on](https://supabase.com/docs/guides/platform/ipv4-address).

The Dedicated Pooler ensures best performance and latency, while using up more of your project's compute resources. If your network supports IPv6 or you have the IPv4 add-on, we encourage you to use the Dedicated Pooler over the Shared Pooler.

PgBouncer always runs in Transaction mode and the current version does not support prepared statement (will be added in a few weeks).

## More about connection pooling[#](#more-about-connection-pooling)

Connection pooling improves database performance by reusing existing connections between queries. This reduces the overhead of establishing connections and improves scalability.

You can use an application-side pooler or a server-side pooler (Supabase automatically provides one called Supavisor), depending on whether your backend is persistent or serverless.

### Application-side poolers[#](#application-side-poolers)

Application-side poolers are built into connection libraries and API servers, such as Prisma, SQLAlchemy, and PostgREST. They maintain several active connections with Postgres or a server-side pooler, reducing the overhead of establishing connections between queries. When deploying to static architecture, such as long-standing containers or VMs, application-side poolers are satisfactory on their own.

### Serverside poolers[#](#serverside-poolers)

Postgres connections are like a WebSocket. Once established, they are preserved until the client (application server) disconnects. A server might only make a single 10 ms query, but needlessly reserve its database connection for seconds or longer.

Serverside-poolers, such as Supabase's [Supavisor](https://github.com/supabase/supavisor) in transaction mode, sit between clients and the database and can be thought of as load balancers for Postgres connections.

They maintain hot connections with the database and intelligently share them with clients only when needed, maximizing the amount of queries a single connection can service. They're best used to manage queries from auto-scaling systems, such as edge and serverless functions.

## Connecting with SSL[#](#connecting-with-ssl)

You should connect to your database using SSL wherever possible, to prevent snooping and man-in-the-middle attacks.

You can obtain your connection info and Server root certificate from your application's dashboard:

![Connection Info and Certificate.](https://supabase.com/docs/img/database/database-settings-ssl.png)

## Resources[#](#resources)

-   [Connection management](https://supabase.com/docs/guides/database/connection-management)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/connecting-to-postgres.mdx)

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