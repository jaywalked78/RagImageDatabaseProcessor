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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Guides

5.  [Integrating with Supabase Auth](https://supabase.com/docs/guides/functions/auth)

# 

Integrating With Supabase Auth

## 

Supabase Edge Functions and Auth.

* * *

Edge Functions work seamlessly with [Supabase Auth](https://supabase.com/docs/guides/auth).

## Auth context[#](#auth-context)

When a user makes a request to an Edge Function, you can use the Authorization header to set the Auth context in the Supabase client:

```
123456789101112131415import { createClient } from 'jsr:@supabase/supabase-js@2'Deno.serve(async (req: Request) => {  const supabaseClient = createClient(    Deno.env.get('SUPABASE_URL') ?? '',    Deno.env.get('SUPABASE_ANON_KEY') ?? '',  );  // Get the session or user object  const authHeader = req.headers.get('Authorization')!;  const token = authHeader.replace('Bearer ', '');  const { data } = await supabaseClient.auth.getUser(token);})
```

Importantly, this is done _inside_ the `Deno.serve()` callback argument, so that the Authorization header is set for each request.

## Fetching the user[#](#fetching-the-user)

After initializing a Supabase client with the Auth context, you can use `getUser()` to fetch the user object, and run queries in the context of the user with [Row Level Security (RLS)](https://supabase.com/docs/guides/database/postgres/row-level-security) policies enforced.

```
123456789101112131415161718192021import { createClient } from 'jsr:@supabase/supabase-js@2'Deno.serve(async (req: Request) => {  const supabaseClient = createClient(    Deno.env.get('SUPABASE_URL') ?? '',    Deno.env.get('SUPABASE_ANON_KEY') ?? '',  )  // Get the session or user object  const authHeader = req.headers.get('Authorization')!  const token = authHeader.replace('Bearer ', '')  const { data } = await supabaseClient.auth.getUser(token)  const user = data.user  return new Response(JSON.stringify({ user }), {    headers: { 'Content-Type': 'application/json' },    status: 200,  })})
```

## Row Level Security[#](#row-level-security)

After initializing a Supabase client with the Auth context, all queries will be executed with the context of the user. For database queries, this means [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) will be enforced.

```
123456789101112131415161718192021import { createClient } from 'jsr:@supabase/supabase-js@2'Deno.serve(async (req: Request) => {  const supabaseClient = createClient(    Deno.env.get('SUPABASE_URL') ?? '',    Deno.env.get('SUPABASE_ANON_KEY') ?? '',  );  // Get the session or user object  const authHeader = req.headers.get('Authorization')!;  const token = authHeader.replace('Bearer ', '');  const { data: userData } = await supabaseClient.auth.getUser(token);  const { data, error } = await supabaseClient.from('profiles').select('*');  return new Response(JSON.stringify({ data }), {    headers: { 'Content-Type': 'application/json' },    status: 200,  })})
```

## Example code[#](#example-code)

See a full [example on GitHub](https://github.com/supabase/supabase/blob/master/examples/edge-functions/supabase/functions/select-from-table-with-auth-rls/index.ts).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/auth.mdx)

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