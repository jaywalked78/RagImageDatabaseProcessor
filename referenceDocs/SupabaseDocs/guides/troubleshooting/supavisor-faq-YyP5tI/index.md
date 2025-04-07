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

# Supavisor FAQ

Last edited: 2/21/2025

* * *

### What problems do poolers solve?[#](#what-problems-do-poolers-solve)

Postgres stands out from other databases by opting to create a new process, not a new thread, for each direct connection. While this design choice brings [numerous benefits](https://www.postgresql.org/message-id/1098894087.31930.62.camel@localhost.localdomain), it introduces a startup penalty for new connections. Moreover, connections are more memory-intensive and can strain Postgres's internal schedulers, limiting the sustainable number that can be formed. Resultingly, developers must be mindful of how they allocate the resource.

When a client (backend server) connects to Postgres, the connection is stateful and enduring, allowing clients to greedily hold onto connections without any obligation to give them up. Typically, applications do not continuously send queries to a database, so this pattern underutilizes finite connections that could have serviced other clients.

PostgreSQL's shortcomings are particularly evident when handling transient servers, like edge functions. They not only hoard connections for brief queries but also aggressively open and close connections, straining the database.

### How do poolers solve the problem?[#](#how-do-poolers-solve-the-problem)

A pooler is ultimately a load balancer for database connections. It maintains several hot connections that it triages to clients. This reduces the startup cost of creating a new process on Postgres. The pooler can also more efficiently manage a database's finite connections by only allowing clients to access them when they need to execute a query (A.K.A. transaction mode).

### Are poolers necessary?[#](#are-poolers-necessary)

All database connection libraries, such as Prisma, SQLAlchemy, and Postgres.js have built-in poolers. These are known as application-side poolers and they are fundamental for sustainable connection management. Most libraries have default pool sizes that may need to be changed for specific workloads. As an example, most edge/serverless functions are called to service a single user's request. They usually require significantly fewer connections (often 1 is optimal) than a dedicated application server.

Note, that like databases, servers can only maintain a certain amount of connections themselves. If you were to increase the number aggressively, the server may not be able gracefully orchestrate them. For instance, Prisma's [default pool size](https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/connection-pool#connection-pool-size) is automatically set to one more than twice the server's CPU count (1 + 2 \* num\_of\_CPUs). The Prisma Team chose this value because it is generally performant with ORM's internal architecture.

When deploying to static architecture, such as long-standing containers or VMs, application-side poolers are satisfactory on their own.

When connecting to your application from serverless/edge functions, horizontally auto-scaling servers, or in cases where you need more connections than what the database can manage, it's best to complement application-side poolers with a serverside one. Supabase provides Supavisor as an option, but you could use alternatives, such as Prisma's Accelerate or Cloudflare's Hyperdrive.

They sit between the database and your client servers. They are solely optimized for sustaining high numbers of client connections and queuing and triaging queries to the database. Although they add network complexity, they are necessary when managing auto-scaling servers that can hypothetically form an infinite amount of connections.

### Where are the connection strings[#](#where-are-the-connection-strings)

Supabase provides 3 database connection strings that can be used simultaneously if necessary. All can be viewed in the connection string section of the [Database Settings](https://supabase.com/dashboard/project/_/settings/database)

![Screenshot 2024-07-04 at 10 40 38 AM](https://github.com/supabase/supabase/assets/91111415/1d653203-84d9-406a-a7c9-1f7d097f5a29)

#### Direct connections:[#](#direct-connections)

> "Note uses an IPv6 address by default. [Check here to see if your network is IPv6 compatible](https://github.com/orgs/supabase/discussions/27034)"

```
12# Example connection stringpostgresql://postgres:[YOUR-PASSWORD]@db.ajrbwkcuthywfihaarmflo.supabase.co:5432/postgres
```

#### Supavisor in transaction mode (port 6543)[#](#supavisor-in-transaction-mode-port-6543)

```
12# Example transaction stringpostgresql://postgres.ajrbwkcuthywddfihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### Supavisor in session mode (port 5432)[#](#supavisor-in-session-mode-port-5432)

```
12# Example session stringpostgresql://postgres.ajrbwkcuthywfddihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### Supavisor: Transaction mode vs. Session mode?[#](#supavisor-transaction-mode-vs-session-mode)

When a client forms a direct connection with Postgres, it usually will make a few queries, but may not utilize the connection the entire time. In transaction mode, a client is allowed to make a single query before being sent back to the figurative "waiting room". This prevents greedy or sedentary clients from hoarding connections. In most cases, this increases query throughput and is optimal.

In session mode, once the pooler assigns a direct connection, it stays with that client until voluntarily surrendered.

This behavior mirrors a direct connection, allowing greedy clients to monopolize the pool. This raises a question: what is the purpose of session mode?

Depending on your application's configurations, having the pooler manage a queue of patient clients is preferable to the alternative of constantly polling the database to check for an available connection. Session mode can queue clients for up to a minute. If this isn't particularly relevant to your application design, then the primary benefit is that it is [IPv4 compatible](https://github.com/orgs/supabase/discussions/27034). Also, unlike transaction mode, it supports prepared statements.

### What happens when a client library, such as Prisma, connects through Supavisor?[#](#what-happens-when-a-client-library-such-as-prisma-connects-through-supavisor)

When clients connect to either Postgres or Supavisor, they do so with the Postgres Wire Protocol. Because of this, clients treat connections with pooler as if they were directly connected to Postgres. The pooler then smoothly acts as a messenger between the database and the client.

### What are "client connections"?[#](#what-are-client-connections)

In summary, they have nothing to do with front-end clients. They are the amount of backend-server connections that can connect to a serverside pooler. Imagine a chess tournament with 60 boards. Each board represents a connection in a database. When a player sits down at a board, it's like a client connecting to the database. They can take their time with their moves or just sit there, not making any.

But when the tournament fills up and all the boards are taken, new players are turned away, and told to check back at a later time to see if a table becomes available.

Now, imagine the tournament organizers decide to expand the venue to house 200 people without adding more tables. Even when all boards are occupied, players don't have to leave. They can wait in the wings, and the moment a board opens up, someone from the waiting area can take their place. Likewise, if someone ends their game, but wants to play again, they can just go back to the waiting area. The waiting area represents the "Max Client Connections". Ultimately, the additional capacity provided by the pooler ensures fewer people are turned away from the "tournament".

### In the context of Supavisor, what does "pool size" mean?[#](#in-the-context-of-supavisor-what-does-pool-size-mean)

"Pool size" refers to the maximum number of direct connections the pooler can maintain per unique user, database, and mode combination. You can adjust it in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) to strike a balance between efficient resource utilization and accommodating peak traffic.

### What is the "user+db+mode" combination?[#](#what-is-the-userdbmode-combination)

Postgres is not actually a database. It is a Relational Database Management System (RDMS). Within it, you can spawn Postgres databases. In Supabase, it is a common pattern to just use the default database called `postgres`, but you could create more:

```
12CREATE DATABASE postgres;CREATE DATABASE another_database;
```

Similarly, a database can have many database users, but most people just rely on the default user `postgres`.

```
12CREATE USER postgres WITH PASSWORD 'super-secret-password;CREATE USER some_new_user WITH PASSWORD 'password';
```

The modes are transaction (port 6543) and session (port 5432) mode.

The "user+database+mode" combinations are formed from the above variables and are used within the connection string:

```
1postgres://[USER].shfmmplnqscentnakbkl:[password]@aws-0-ca-central-1.pooler.supabase.com:[MODE]/[DATABASE]
```

When a distinct combination connects to your database, a new direct connection pool will be created. That means if you have two combinations connecting and the "Pool Size" is set to 120, each combination will have permission to form 120 connections. This can become problematic if collectively they exhaust all available direct connections.

### **Does Supavisor immediately establish the max pool size?**[#](#does-supavisor-immediately-establish-the-max-pool-size)

No, it doesn't. Let's break it down:

-   In transaction mode, the pooler will only add connections if there are not enough connections to service all pending queries simultaneously. If 10 clients connect, but a single direct connection can comfortably accommodate them all, the pooler will not create more.
-   If necessary, it can create as many connections to prevent queries from pending up to the limit specified by the "Pool Size".
-   In session mode, it will immediately create a new a direct connection for a new client unless the "Pool Size" is reached
-   In transaction mode, once a direct connection is established, the pooler will keep it available for reuse for another client. However, if the connection remains unused for 5 minutes, the pooler will close it to free up database resources. In session mode, the connection will be immediately closed.
-   If a client is connected to the pooler, then at least 1 hot connection will be sustained, even if no client needs it.

### **How to change pool size**[#](#how-to-change-pool-size)

In the [Dashboard's Database Settings](https://supabase.com/dashboard/project/_/settings/database), you can configure Supavisor's "Pool Size":

![Screenshot 2024-02-25 at 10 06 25 PM](https://github.com/supabase/supabase/assets/91111415/ce9e9d28-67c2-4dd2-ac0a-0a0150e63b4f)

You can also change the pool size for PostgREST's (DB API) internal pooler at the bottom of the [application settings](https://supabase.com/dashboard/project/_/settings/api).

### Do all services on Supabase use Supavisor?[#](#do-all-services-on-supabase-use-supavisor)

Supabase Storage uses Supavisor internally. The other servers that communicate with Postgres (PostgREST, Realtime, and Auth) all rely on internal application poolers.

Supavisor is primarily intended for users who do not want to rely on the Supabase Client libraries and instead prefer to work with external ORMs, such as Prisma, Drizzle, and Psycopg.

### **Whether to change Supavisor's pool size?**[#](#whether-to-change-supavisors-pool-size)

In an ideal scenario, Postgres would support an unlimited number of direct connections, but there's a limit to how many it can handle. If Supavisor uses most of the available connections, you risk depriving other servers, such as Auth, from accessing your database. Still, as much as possible, you want to give your pooler freedom to grow its pool as needed to service demand.

It's important to note that the Storage server also uses Supavisor as a unique "user+db+mode" combination, so the pool size you set for your general application will apply to it, too.

As a rule of thumb, if you're using the DB REST API or multiple app-based "user+db+mode" combinations, try to keep the pooler's usage under 40% of available connections. Otherwise, you can cautiously increase usage to around 80%. These percentages are flexible and depend on your application's usage and setup. Monitor connection usage to determine the optimal allocation without depriving other servers of necessary connections.

### **How to monitor connections**[#](#how-to-monitor-connections)

> EDIT: a more in-depth [troubleshooting guide](https://github.com/orgs/supabase/discussions/27141) for connection monitoring was published

Connection usage can be monitored with a Supabase Grafana Dashboard. It provides realtime visibility of over 200 database metrics, such as graphs of CPU, EBS, and active direct/pooler connections. It can be extremely useful for monitoring and debugging instances.

You can check our [GitHub repo](https://github.com/supabase/supabase-grafana) for setup instructions for local deployments or free cloud deployments on [Fly.io](http://fly.io/). Refer to Supabase [documentation](https://supabase.com/docs/guides/platform/metrics) to learn more about the metrics endpoint.

### **Can Supavisor really support a million connections?**[#](#can-supavisor-really-support-a-million-connections)

It depends.

In the article ["Supavisor: Scaling Postgres to 1 Million Connections"](https://supabase.com/blog/supavisor-1-million) we gave Supavisor the capacity to connect to a million clients simultaneously. The pooler triaged the clients' queries to 400 database connections.

What is important is that the database processing these queries had 64vCPUs and 256GB of memory. It could process the queries fast enough to ensure that there was never a noticeable bottleneck. The clients never waited long enough to timeout. If the clients were asking to run inefficient queries, like the one below, a severe backlog of pending client queries would have formed:

```
12-- do nothing for 60 secondsselect pg_sleep(60);
```

A backlog could also happen if there are not enough direct connections available. In our setup, 400 connections were enough to handle a million clients, ensuring a smooth flow of requests. But if we had only 1 direct connection, the queue would've moved too slowly and clients would expire their requests.

Scaling to this level only works when the pooler is operating in transaction mode. In Session mode, hypothetically, the 400 clients that first accessed the direct connections could keep them, even if they are no longer executing queries. The pending 999,600 clients waiting for a turn would then be starved of direct connections.

## Metadata

* * *

### Products

[Supavisor](https://supabase.com/docs/guides/troubleshooting?products=supavisor)[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[pooler](https://supabase.com/docs/guides/troubleshooting?tags=pooler)[connections](https://supabase.com/docs/guides/troubleshooting?tags=connections)[supavisor](https://supabase.com/docs/guides/troubleshooting?tags=supavisor)[database](https://supabase.com/docs/guides/troubleshooting?tags=database)

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