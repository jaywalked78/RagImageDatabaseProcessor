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

5.  [Drizzle](https://supabase.com/docs/guides/database/drizzle)

# 

Drizzle

* * *

### Connecting with Drizzle[#](#connecting-with-drizzle)

[Drizzle ORM](https://github.com/drizzle-team/drizzle-orm) is a TypeScript ORM for SQL databases designed with maximum type safety in mind. You can use their ORM to connect to your database.

If you plan on solely using Drizzle instead of the Supabase Data API (PostgREST), you can turn off the latter in the [API Settings](https://supabase.com/dashboard/project/_/settings/api).

1

### Install

Install Drizzle and related dependencies.

```
12npm i drizzle-orm postgresnpm i -D drizzle-kit
```

2

### Create your models

Create a `schema.ts` file and define your models.

```
1234567import { pgTable, serial, text, varchar } from "drizzle-orm/pg-core";export const users = pgTable('users', {  id: serial('id').primaryKey(),  fullName: text('full_name'),  phone: varchar('phone', { length: 256 }),});
```

3

### Connect

Connect to your database using the Connection Pooler.

In your [`Database Settings`](https://supabase.com/dashboard/project/_/settings/database), make sure `Use connection pooler` is checked, then copy the URI and save it as the `DATABASE_URL` environment variable. Remember to replace the password placeholder with your actual database password.

```
12345678910import 'dotenv/config'import { drizzle } from 'drizzle-orm/postgres-js'import postgres from 'postgres'const connectionString = process.env.DATABASE_URL// Disable prefetch as it is not supported for "Transaction" pool modeexport const client = postgres(connectionString, { prepare: false })export const db = drizzle(client);
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/drizzle.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)