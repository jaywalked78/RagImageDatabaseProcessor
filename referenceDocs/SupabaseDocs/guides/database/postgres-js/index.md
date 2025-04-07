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

3.  ORM Quickstarts

5.  [Postgres.js](https://supabase.com/docs/guides/database/postgres-js)

# 

Postgres.js

* * *

### Connecting with Postgres.js[#](#connecting-with-postgresjs)

[Postgres.js](https://github.com/porsager/postgres) is a full-featured Postgres client for Node.js and Deno.

1

### Install

Install Postgres.js and related dependencies.

```
1npm i postgres
```

2

### Connect

Create a `db.js` file with the connection details.

To get your connection details, go to your [`Database Settings`](https://supabase.com/dashboard/project/_/settings/database). Make sure `Use connection pooling` is enabled. Choose `Transaction Mode` if you're on a platform with transient connections, such as a serverless function, and `Session Mode` if you have a long-lived connection. Copy the URI and save it as the environment variable `DATABASE_URL`.

```
1234567// db.jsimport postgres from 'postgres'const connectionString = process.env.DATABASE_URLconst sql = postgres(connectionString)export default sql
```

3

### Execute commands

Use the connection to execute commands.

```
1234567891011import sql from './db.js'async function getUsersOver(age) {  const users = await sql`    select name, age    from users    where age > ${ age }  `  // users = Result [{ name: "Walter", age: 80 }, { name: 'Murray', age: 68 }, ...]  return users}
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres-js.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)