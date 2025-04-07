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

5.  [SolidJS](https://supabase.com/docs/guides/getting-started/quickstarts/solidjs)

# 

Use Supabase with SolidJS

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from a SolidJS app.

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

### Create a SolidJS app

Create a SolidJS app using the `degit` command.

```
1npx degit solidjs/templates/js my-app
```

3

### Install the Supabase client library

The fastest way to get started is to use the `supabase-js` client library which provides a convenient interface for working with Supabase from a SolidJS app.

Navigate to the SolidJS app and install `supabase-js`.

```
1cd my-app && npm install @supabase/supabase-js
```

4

### Query data from the app

In `App.jsx`, create a Supabase client using your project URL and public API (anon) key:

###### Project URL

Loading...

###### Anon key

Loading...

Add a `getInstruments` function to fetch the data and display the query result to the page.

```
123456789101112131415161718192021import { createClient } from "@supabase/supabase-js";  import { createResource, For } from "solid-js";  const supabase = createClient('https://<project>.supabase.co', '<your-anon-key>');  async function getInstruments() {    const { data } = await supabase.from("instruments").select();    return data;  }  function App() {    const [instruments] = createResource(getInstruments);    return (      <ul>        <For each={instruments()}>{(instrument) => <li>{instrument.name}</li>}</For>      </ul>    );  }  export default App;
```

5

### Start the app

Start the app and go to [http://localhost:3000](http://localhost:3000) in a browser and you should see the list of instruments.

```
1npm run dev
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/solidjs.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)