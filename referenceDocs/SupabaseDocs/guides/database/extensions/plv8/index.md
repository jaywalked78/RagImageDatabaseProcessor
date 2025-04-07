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

3.  Extensions

5.  [plv8: Javascript Language](https://supabase.com/docs/guides/database/extensions/plv8)

# 

plv8: JavaScript Language

* * *

The `plv8` extension allows you use JavaScript within Postgres.

## Overview[#](#overview)

While Postgres natively runs SQL, it can also run other procedural languages. `plv8` allows you to run JavaScript code - specifically any code that runs on the [V8 JavaScript engine](https://v8.dev).

It can be used for database functions, triggers, queries and more.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "plv8" and enable the extension.

## Create `plv8` functions[#](#create-plv8-functions)

Functions written in `plv8` are written just like any other Postgres functions, only with the `language` identifier set to `plv8`.

```
123456create or replace function function_name()returns void as $$    // V8 JavaScript    // code    // here$$ language plv8;
```

You can call `plv8` functions like any other Postgres function:

SQLJavaScriptKotlin

```
1select function_name();
```

## Examples[#](#examples)

### Scalar functions[#](#scalar-functions)

A [scalar function](https://plv8.github.io/#scalar-function-calls) is anything that takes in some user input and returns a single result.

```
1234567create or replace function hello_world(name text)returns text as $$    let output = `Hello, ${name}!`;    return output;$$ language plv8;
```

### Executing SQL[#](#executing-sql)

You can execute SQL within `plv8` code using the [`plv8.execute` function](https://plv8.github.io/#plv8-execute).

```
12345678910create or replace function update_user(id bigint, first_name text)returns smallint as $$    var num_affected = plv8.execute(        'update profiles set first_name = $1 where id = $2',        [first_name, id]    );    return num_affected;$$ language plv8;
```

### Set-returning functions[#](#set-returning-functions)

A [set-returning function](https://plv8.github.io/#set-returning-function-calls) is anything that returns a full set of results - for example, rows in a table.

```
1234567891011create or replace function get_messages()returns setof messages as $$    var json_result = plv8.execute(        'select * from messages'    );    return json_result;$$ language plv8;select * from get_messages();
```

## Resources[#](#resources)

-   Official [`plv8` documentation](https://plv8.github.io/)
-   [plv8 GitHub Repository](https://github.com/plv8/plv8)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/plv8.mdx)

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