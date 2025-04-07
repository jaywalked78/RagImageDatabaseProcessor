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

3.  Getting started

5.  [Development tips](https://supabase.com/docs/guides/functions/development-tips)

# 

Development tips

## 

Tips for getting started with Edge Functions.

* * *

Here are a few recommendations when you first start developing Edge Functions.

### Skipping authorization checks[#](#skipping-authorization-checks)

By default, Edge Functions require a valid JWT in the authorization header. If you want to use Edge Functions without Authorization checks (commonly used for Stripe webhooks), you can pass the `--no-verify-jwt` flag when serving your Edge Functions locally.

```
1supabase functions serve hello-world --no-verify-jwt
```

Be careful when using this flag, as it will allow anyone to invoke your Edge Function without a valid JWT. The Supabase client libraries automatically handle authorization.

### Using HTTP methods[#](#using-http-methods)

Edge Functions support `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, and `OPTIONS`. A Function can be designed to perform different actions based on a request's HTTP method. See the [example on building a RESTful service](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/restful-tasks) to learn how to handle different HTTP methods in your Function.

##### HTML not supported

HTML content is not supported. `GET` requests that return `text/html` will be rewritten to `text/plain`.

### Naming Edge Functions[#](#naming-edge-functions)

We recommend using hyphens to name functions because hyphens are the most URL-friendly of all the naming conventions (snake\_case, camelCase, PascalCase).

### Organizing your Edge Functions[#](#organizing-your-edge-functions)

We recommend developing "fat functions". This means that you should develop few large functions, rather than many small functions. One common pattern when developing Functions is that you need to share code between two or more Functions. To do this, you can store any shared code in a folder prefixed with an underscore (`_`). We also recommend a separate folder for [Unit Tests](https://supabase.com/docs/guides/functions/unit-test) including the name of the function followed by a `-test` suffix. We recommend this folder structure:

```
12345678910111213141516└── supabase    ├── functions    │   ├── import_map.json # A top-level import map to use across functions.    │   ├── _shared    │   │   ├── supabaseAdmin.ts # Supabase client with SERVICE_ROLE key.    │   │   └── supabaseClient.ts # Supabase client with ANON key.    │   │   └── cors.ts # Reusable CORS headers.    │   ├── function-one # Use hyphens to name functions.    │   │   └── index.ts    │   └── function-two    │   │   └── index.ts    │   └── tests    │       └── function-one-test.ts    │       └── function-two-test.ts    ├── migrations    └── config.toml
```

### Using config.toml[#](#using-configtoml)

Individual function configuration like [JWT verification](https://supabase.com/docs/guides/cli/config#functions.function_name.verify_jwt) and [import map location](https://supabase.com/docs/guides/cli/config#functions.function_name.import_map) can be set via the `config.toml` file.

```
123[functions.hello-world]verify_jwt = falseimport_map = './import_map.json'
```

### Not using TypeScript[#](#not-using-typescript)

When you create a new Edge Function, it will use TypeScript by default. However, it is possible to write and deploy Edge Functions using pure JavaScript.

Save your Function as a JavaScript file (e.g. `index.js`) and then update the `supabase/config.toml` as follows:

`entrypoint` is available only in Supabase CLI version 1.215.0 or higher.

```
123[functions.hello-world]# other entriesentrypoint = './functions/hello-world/index.js' # path must be relative to config.toml
```

You can use any `.ts`, `.js`, `.tsx`, `.jsx` or `.mjs` file as the `entrypoint` for a Function.

### Error handling[#](#error-handling)

The `supabase-js` library provides several error types that you can use to handle errors that might occur when invoking Edge Functions:

```
123456789101112131415import { FunctionsHttpError, FunctionsRelayError, FunctionsFetchError } from '@supabase/supabase-js'const { data, error } = await supabase.functions.invoke('hello', {  headers: { 'my-custom-header': 'my-custom-header-value' },  body: { foo: 'bar' },})if (error instanceof FunctionsHttpError) {  const errorMessage = await error.context.json()  console.log('Function returned an error', errorMessage)} else if (error instanceof FunctionsRelayError) {  console.log('Relay error:', error.message)} else if (error instanceof FunctionsFetchError) {  console.log('Fetch error:', error.message)}
```

### Database Functions vs Edge Functions[#](#database-functions-vs-edge-functions)

For data-intensive operations we recommend using [Database Functions](https://supabase.com/docs/guides/database/functions), which are executed within your database and can be called remotely using the [REST and GraphQL API](https://supabase.com/docs/guides/api).

For use-cases which require low-latency we recommend [Edge Functions](https://supabase.com/docs/guides/functions), which are globally-distributed and can be written in TypeScript.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/development-tips.mdx)

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