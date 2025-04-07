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

5.  [React](https://supabase.com/docs/guides/getting-started/quickstarts/reactjs)

# 

Use Supabase with React

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from a React app.

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

### Create a React app

Create a React app using a [Vite](https://vitejs.dev/guide/) template.

```
1npm create vite@latest my-app -- --template react
```

3

### Install the Supabase client library

The fastest way to get started is to use the `supabase-js` client library which provides a convenient interface for working with Supabase from a React app.

Navigate to the React app and install `supabase-js`.

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
123456789101112131415161718192021222324252627import { useEffect, useState } from "react";  import { createClient } from "@supabase/supabase-js";  const supabase = createClient("https://<project>.supabase.co", "<your-anon-key>");  function App() {    const [instruments, setInstruments] = useState([]);    useEffect(() => {      getInstruments();    }, []);    async function getInstruments() {      const { data } = await supabase.from("instruments").select();      setInstruments(data);    }    return (      <ul>        {instruments.map((instrument) => (          <li key={instrument.name}>{instrument.name}</li>        ))}      </ul>    );  }  export default App;
```

5

### Start the app

Start the app, go to [http://localhost:5173](http://localhost:5173) in a browser, and open the browser console and you should see the list of instruments.

```
1npm run dev
```

## Next steps[#](#next-steps)

-   Set up [Auth](https://supabase.com/docs/guides/auth) for your app
-   [Insert more data](https://supabase.com/docs/guides/database/import-data) into your database
-   Upload and serve static files using [Storage](https://supabase.com/docs/guides/storage)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/reactjs.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)