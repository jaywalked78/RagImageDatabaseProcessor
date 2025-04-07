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

5.  [Handling Routing in Functions](https://supabase.com/docs/guides/functions/routing)

# 

Handling Routing in Functions

## 

How to handle custom routing within Edge Functions.

* * *

Usually, an Edge Function is written to perform a single action (e.g. write a record to the database). However, if your app's logic is split into multiple Edge Functions requests to each action may seem slower. This is because each Edge Function needs to be booted before serving a request (known as cold starts). If an action is performed less frequently (e.g. deleting a record), there is a high-chance of that function experiencing a cold-start.

One way to reduce the cold starts and increase performance of your app is to combine multiple actions into a single Edge Function. This way only one instance of the Edge Function needs to be booted and it can handle multiple requests to different actions. For example, we can use a single Edge Function to create a typical CRUD API (create, read, update, delete records).

To combine multiple endpoints into a single Edge Function, you can use web application frameworks such as [Express](https://expressjs.com/), [Oak](https://oakserver.github.io/oak/), or [Hono](https://hono.dev).

Let's dive into some examples.

## Routing with frameworks[#](#routing-with-frameworks)

Here's a simple hello world example using some popular web frameworks.

Create a new function called `hello-world` using Supabase CLI:

```
1supabase functions new hello-world
```

Copy and paste the following code:

ExpressOakHonoDeno

```
1234567891011121314import { Hono } from 'jsr:@hono/hono';const app = new Hono();app.post('/hello-world', async (c) => {  const { name } = await c.req.json();  return new Response(`Hello ${name}!`)});app.get('/hello-world', (c) => {  return new Response('Hello World!')});Deno.serve(app.fetch);
```

You will notice in the above example, we created two routes - `GET` and `POST`. The path for both routes are defined as `/hello-world`. If you run a server outside of Edge Functions, you'd usually set the root path as `/` . However, within Edge Functions, paths should always be prefixed with the function name (in this case `hello-world`).

You can deploy the function to Supabase via:

```
1supabase functions deploy hello-world
```

Once the function is deployed, you can try to call the two endpoints using cURL (or Postman).

```
123# https://supabase.com/docs/guides/functions/deploy#invoking-remote-functionscurl --request GET 'https://<project_ref>.supabase.co/functions/v1/hello-world' \  --header 'Authorization: Bearer ANON_KEY' \
```

This should print the response as `Hello World!`, meaning it was handled by the `GET` route.

Similarly, we can make a request to the `POST` route.

```
12345# https://supabase.com/docs/guides/functions/deploy#invoking-remote-functionscurl --request POST 'https://<project_ref>.supabase.co/functions/v1/hello-world' \  --header 'Authorization: Bearer ANON_KEY' \  --header 'Content-Type: application/json' \  --data '{ "name":"Foo" }'
```

We should see a response printing `Hello Foo!`.

## Using route parameters[#](#using-route-parameters)

We can use route parameters to capture values at specific URL segments (e.g. `/tasks/:taskId/notes/:noteId`).

Here's an example Edge Function implemented using the Framework for managing tasks using route parameters. Keep in mind paths must be prefixed by function name (i.e. `tasks` in this example). Route parameters can only be used after the function name prefix.

ExpressOakHonoDeno

## URL patterns API[#](#url-patterns-api)

If you prefer not to use a web framework, you can directly use [URL Pattern API](https://developer.mozilla.org/en-US/docs/Web/API/URL_Pattern_API) within your Edge Functions to implement routing. This is ideal for small apps with only couple of routes and you want to have a custom matching algorithm.

Here is an example Edge Function using URL Patterns API: [https://github.com/supabase/supabase/blob/master/examples/edge-functions/supabase/functions/restful-tasks/index.ts](https://github.com/supabase/supabase/blob/master/examples/edge-functions/supabase/functions/restful-tasks/index.ts)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/routing.mdx)

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