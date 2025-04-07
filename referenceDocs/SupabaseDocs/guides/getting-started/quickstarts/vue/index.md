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

5.  [Vue](https://supabase.com/docs/guides/getting-started/quickstarts/vue)

# 

Use Supabase with Vue

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from a Vue app.

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

### Create a Vue app

Create a Vue app using the `npm init` command.

```
1npm init vue@latest my-app
```

3

### Install the Supabase client library

The fastest way to get started is to use the `supabase-js` client library which provides a convenient interface for working with Supabase from a Vue app.

Navigate to the Vue app and install `supabase-js`.

```
1cd my-app && npm install @supabase/supabase-js
```

4

### Create the Supabase client

Create a `/src/lib` directory in your Vue app, create a file called `supabaseClient.js` and add the following code to initialize the Supabase client with your project URL and public API (anon) key:

###### Project URL

Loading...

###### Anon key

Loading...

```
123import { createClient } from '@supabase/supabase-js'  export const supabase = createClient('https://<project>.supabase.co', '<your-anon-key>')
```

5

### Query data from the app

Replace the existing content in your `App.vue` file with the following code.

```
123456789101112131415161718192021<script setup>  import { ref, onMounted } from 'vue'  import { supabase } from './lib/supabaseClient'  const instruments = ref([])  async function getInstruments() {    const { data } = await supabase.from('instruments').select()    instruments.value = data  }  onMounted(() => {    getInstruments()  })  </script>  <template>    <ul>      <li v-for="instrument in instruments" :key="instrument.id">{{ instrument.name }}</li>    </ul>  </template>
```

6

### Start the app

Start the app and go to [http://localhost:5173](http://localhost:5173) in a browser and you should see the list of instruments.

```
1npm run dev
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/vue.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)