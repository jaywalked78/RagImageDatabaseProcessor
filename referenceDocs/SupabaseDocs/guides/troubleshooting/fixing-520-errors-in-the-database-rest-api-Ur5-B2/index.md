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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Fixing 520 Errors in the Database REST API

Last edited: 1/17/2025

* * *

In the context of the database API, [Cloudflare 520 errors](https://developers.cloudflare.com/support/troubleshooting/cloudflare-errors/troubleshooting-cloudflare-5xx-errors/#error-520-web-server-returns-an-unknown-error) most often occur when 16+KB worth of data is present in the headers/URL of your requests.

The API will include filters within the URL, so a request like so:

```
1let { data: countries, error } = await supabase.from('countries').select('name')
```

translates to a URL like:

```
1https://<project ref>.supabase.co/rest/v1/countries?select=name
```

However, appending too much data to the URL can exceed the 16KB limitation, triggering a 520 failure. This typically occurs with lengthy `in` clauses, as demonstrated here:

```
1234const { data, error } = await supabase  .from('countries')  .select()  .not('id', 'in', '(5,6,7,8,9,...10,000)')
```

To circumvent this issue, you must use [RPCs](https://supabase.com/docs/reference/javascript/explain?queryGroups=example&example=call-a-postgres-function-with-arguments). They are database functions that you can call from the API. Instead of including a query's structure within the URL or header, they move it into the request's payload.

Here is a basic example of a [database function](https://supabase.com/docs/guides/database/functions)

```
123456789create or replace function example(id uuid[])returns uuid[]language plpgsqlas $$begin raise log 'the function example was called with an array size of: %', (select array_length(id, 1)); return id;end;$$;
```

The [RPC](https://supabase.com/docs/reference/javascript/explain?queryGroups=example&example=call-a-postgres-function-with-arguments) can then call the function with an array that contains more than 16KB of data

```
1const { data, error } = await supabase.rpc('example', { id: ['e2f34fb9-bbf9-4649-9b2f-09ec56e67a42', ...900 more UUIDs] })
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[520](https://supabase.com/docs/guides/troubleshooting?errorCodes=520)

* * *

### Tags

[520](https://supabase.com/docs/guides/troubleshooting?tags=520)[cloudflare](https://supabase.com/docs/guides/troubleshooting?tags=cloudflare)[url](https://supabase.com/docs/guides/troubleshooting?tags=url)[headers](https://supabase.com/docs/guides/troubleshooting?tags=headers)[rpcs](https://supabase.com/docs/guides/troubleshooting?tags=rpcs)

* * *

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