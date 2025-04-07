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

Getting Started

1.  [Start with Supabase](https://supabase.com/docs/guides/getting-started)

3.  Framework Quickstarts

5.  [Next.js](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)

# 

Use Supabase with Next.js

## 

Learn how to create a Supabase project, add some sample data, and query from a Next.js app.

* * *

1

### Create a Supabase project

Go to [database.new](https://database.new) and create a new Supabase project.

When your project is up and running, go to the [Table Editor](https://supabase.com/dashboard/project/_/editor), create a new table and insert some data.

Alternatively, you can run the following snippet in your project's [SQL Editor](https://supabase.com/dashboard/project/_/sql/new). This will create a `instruments` table with some sample data.

```
12345678910111213-- Create the tablecreate table instruments (  id bigint primary key generated always as identity,  name text not null);-- Insert some sample data into the tableinsert into instruments (name)values  ('violin'),  ('viola'),  ('cello');alter table instruments enable row level security;
```

Make the data in your table publicly readable by adding an RLS policy:

```
1234create policy "public can read instruments"on public.instrumentsfor select to anonusing (true);
```

2

### Create a Next.js app

Use the `create-next-app` command and the `with-supabase` template, to create a Next.js app pre-configured with:

-   [Cookie-based Auth](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)
-   [TypeScript](https://www.typescriptlang.org/)
-   [Tailwind CSS](https://tailwindcss.com/)

```
1npx create-next-app -e with-supabase
```

3

### Declare Supabase Environment Variables

Rename `.env.example` to `.env.local` and populate with your Supabase connection variables:

###### Project URL

Loading...

###### Anon key

Loading...

.env.local

```
12NEXT_PUBLIC_SUPABASE_URL=<SUBSTITUTE_SUPABASE_URL>NEXT_PUBLIC_SUPABASE_ANON_KEY=<SUBSTITUTE_SUPABASE_ANON_KEY>
```

4

### Query Supabase data from Next.js

Create a new file at `app/instruments/page.tsx` and populate with the following.

This will select all the rows from the `instruments` table in Supabase and render them on the page.

app/instruments/page.tsxutils/supabase/server.ts

```
12345678import { createClient } from '@/utils/supabase/server';export default async function Instruments() {  const supabase = await createClient();  const { data: instruments } = await supabase.from("instruments").select();  return <pre>{JSON.stringify(instruments, null, 2)}</pre>}
```

5

### Start the app

Run the development server, go to [http://localhost:3000/instruments](http://localhost:3000/instruments) in a browser and you should see the list of instruments.

```
1npm run dev
```

## Next steps[#](#next-steps)

-   Set up [Auth](https://supabase.com/docs/guides/auth) for your app
-   [Insert more data](https://supabase.com/docs/guides/database/import-data) into your database
-   Upload and serve static files using [Storage](https://supabase.com/docs/guides/storage)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/nextjs.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)