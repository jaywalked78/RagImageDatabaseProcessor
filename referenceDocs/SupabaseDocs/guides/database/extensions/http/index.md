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

5.  [http: RESTful Client](https://supabase.com/docs/guides/database/extensions/http)

# 

http: RESTful Client

* * *

The `http` extension allows you to call RESTful endpoints within Postgres.

## Quick demo[#](#quick-demo)

## Overview[#](#overview)

Let's cover some basic concepts:

-   REST: stands for REpresentational State Transfer. It's a way to request data from external services.
-   RESTful APIs are servers which accept HTTP "calls". The calls are typically:
    -   `GET` − Read only access to a resource.
    -   `POST` − Creates a new resource.
    -   `DELETE` − Removes a resource.
    -   `PUT` − Updates an existing resource or creates a new resource.

You can use the `http` extension to make these network requests from Postgres.

## Usage[#](#usage)

### Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `http` and enable the extension.

### Available functions[#](#available-functions)

While the main usage is `http('http_request')`, there are 5 wrapper functions for specific functionality:

-   `http_get()`
-   `http_post()`
-   `http_put()`
-   `http_delete()`
-   `http_head()`

### Returned values[#](#returned-values)

A successful call to a web URL from the `http` extension returns a record with the following fields:

-   `status`: integer
-   `content_type`: character varying
-   `headers`: http\_header\[\]
-   `content`: character varying. Typically you would want to cast this to `jsonb` using the format `content::jsonb`

## Examples[#](#examples)

### Simple `GET` example[#](#simple-get-example)

```
1234select  "status", "content"::jsonbfrom  http_get('https://jsonplaceholder.typicode.com/todos/1');
```

### Simple `POST` example[#](#simple-post-example)

```
12345678select  "status", "content"::jsonbfrom  http_post(    'https://jsonplaceholder.typicode.com/posts',    '{ "title": "foo", "body": "bar", "userId": 1 }',    'application/json'  );
```

## Resources[#](#resources)

-   Official [`http` GitHub Repository](https://github.com/pramsey/pgsql-http)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/http.mdx)

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