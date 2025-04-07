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

REST API

1.  [REST API](https://supabase.com/docs/guides/api)

3.  [Quickstart](https://supabase.com/docs/guides/api/quickstart)

# 

Build an API route in less than 2 minutes.

## 

Create your first API route by creating a table called `todos` to store tasks.

* * *

Let's create our first REST route which we can query using `cURL` or the browser.

We'll create a database table called `todos` for storing tasks. This creates a corresponding API route `/rest/v1/todos` which can accept `GET`, `POST`, `PATCH`, & `DELETE` requests.

1

### Set up a Supabase project with a 'todos' table

[Create a new project](https://supabase.com/dashboard) in the Supabase Dashboard.

After your project is ready, create a table in your Supabase database. You can do this with either the Table interface or the [SQL Editor](https://supabase.com/dashboard/project/_/sql).

SQLDashboard

```
123456-- Create a table called "todos"-- with a column to store tasks.create table todos (  id serial primary key,  task text);
```

2

### Allow public access

Let's turn on Row Level Security for this table and allow public access.

```
12345678910-- Turn on securityalter table "todos"enable row level security;-- Allow anonymous accesscreate policy "Allow public access"  on todos  for select  to anon  using (true);
```

3

### Insert some dummy data

Now we can add some data to our table which we can access through our API.

```
123456insert into todos (task)values  ('Create tables'),  ('Enable security'),  ('Add data'),  ('Fetch data from the API');
```

4

### Fetch the data

Find your API URL and Keys in your Dashboard [API Settings](https://supabase.com/dashboard/project/_/settings/api). You can now query your "todos" table by appending `/rest/v1/todos` to the API URL.

Copy this block of code, substitute `<PROJECT_REF>` and `<ANON_KEY>`, then run it from a terminal.

```
123curl 'https://<PROJECT_REF>.supabase.co/rest/v1/todos' \-H "apikey: <ANON_KEY>" \-H "Authorization: Bearer <ANON_KEY>"
```

## Bonus[#](#bonus)

There are several options for accessing your data:

### Browser[#](#browser)

You can query the route in your browser, by appending the `anon` key as a query parameter:

`https://<PROJECT_REF>.supabase.co/rest/v1/todos?apikey=<ANON_KEY>`

### Client libraries[#](#client-libraries)

We provide a number of [Client Libraries](https://github.com/supabase/supabase#client-libraries).

JavaScriptDartPythonSwift

```
1const { data, error } = await supabase.from('todos').select()
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/api/quickstart.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)