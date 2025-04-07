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

5.  [Prisma](https://supabase.com/docs/guides/database/prisma)

# 

Prisma

* * *

This quickly shows how to connect your Prisma application to Supabase Postgres. If you encounter any problems, reference the [Prisma troubleshooting docs](https://supabase.com/docs/guides/database/prisma/prisma-troubleshooting).

If you plan to solely use Prisma instead of the Supabase Data API (PostgREST), turn it off in the [API Settings](https://supabase.com/dashboard/project/_/settings/api).

1

### Create a custom user for Prisma

-   In the [SQL Editor](https://supabase.com/dashboard/project/_/sql/new), create a Prisma DB user with full privileges on the public schema.
-   This gives you better control over Prisma's access and makes it easier to monitor using Supabase tools like the [Query Performance Dashboard](https://supabase.com/dashboard/project/_/advisors/query-performance) and [Log Explorer](https://supabase.com/dashboard/project/_/logs/explorer).

##### password manager

For security, consider using a [password generator](https://bitwarden.com/password-generator/) for the Prisma role.

```
123456789101112131415-- Create custom usercreate user "prisma" with password 'custom_password' bypassrls createdb;-- extend prisma's privileges to postgres (necessary to view changes in Dashboard)grant "prisma" to "postgres";-- Grant it necessary permissions over the relevant schemas (public)grant usage on schema public to prisma;grant create on schema public to prisma;grant all on all tables in schema public to prisma;grant all on all routines in schema public to prisma;grant all on all sequences in schema public to prisma;alter default privileges for role postgres in schema public grant all on tables to prisma;alter default privileges for role postgres in schema public grant all on routines to prisma;alter default privileges for role postgres in schema public grant all on sequences to prisma;
```

```
12-- alter prisma password if neededalter user "prisma" with password 'new_password';
```

2

### Create a Prisma Project

Create a new Prisma Project on your computer

Create a new directory

```
12mkdir hello-prismacd hello-prisma
```

Initiate a new Prisma project

npmpnpmyarnbun

```
123456npm init -ynpm install prisma typescript ts-node @types/node --save-devnpx tsc --initnpx prisma init
```

3

### Add your connection information to your .env file

-   Visit the [Database Settings](https://supabase.com/dashboard/project/_/settings/database)
-   Find your Supavisor Session Mode string. It should end with 5432. It will be used in your `.env` file.

If you're in an [IPv6 environment](https://github.com/orgs/supabase/discussions/27034) or have the IPv4 Add-On, you can use the direct connection string instead of Supavisor in Session mode.

-   If you plan on deploying Prisma to a serverless or auto-scaling environment, you'll also need your Supavisor transaction mode string.
-   The string is identical to the session mode string but uses port 6543 at the end.

server-based deploymentsserverless deployments

In your .env file, set the DATABASE\_URL variable to your connection string

```
12# Used for Prisma Migrations and within your applicationDATABASE_URL="postgres://[DB-USER].[PROJECT-REF]:[PRISMA-PASSWORD]@[DB-REGION].pooler.supabase.com:5432/postgres"
```

Change your string's `[DB-USER]` to `prisma` and add the password you created in step 1

```
1postgres://prisma.[PROJECT-REF]...
```

4

### Create your migrations

If you have already modified your Supabase database, synchronize it with your migration file. Otherwise create new tables for your database

New ProjectsPopulated Projects

Create new tables in your prisma.schema file

```
123456789101112131415model Post {  id        Int     @id @default(autoincrement())  title     String  content   String?  published Boolean @default(false)  author    User?   @relation(fields: [authorId], references: [id])  authorId  Int?}model User {  id    Int     @id @default(autoincrement())  email String  @unique  name  String?  posts Post[]}
```

commit your migration

npmpnpmyarnbun

```
1npx prisma migrate dev --name first_prisma_migration
```

5

### Install the prisma client

Install the Prisma client and generate its model

npmpnpmyarnbun

```
12npm install @prisma/clientnpx prisma generate
```

6

### Test your API

Create a index.ts file and run it to test your connection

```
123456789101112131415161718192021const { PrismaClient } = require('@prisma/client');const prisma = new PrismaClient();async function main() {  //change to reference a table in your schema  const val = await prisma.<SOME_TABLE_NAME>.findMany({    take: 10,  });  console.log(val);}main()  .then(async () => {    await prisma.$disconnect();  })  .catch(async (e) => {    console.error(e);    await prisma.$disconnect();  process.exit(1);});
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/prisma.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)