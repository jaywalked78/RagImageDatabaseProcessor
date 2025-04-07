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

5.  [Using Deno 2](https://supabase.com/docs/guides/functions/deno2)

# 

Using Deno 2

## 

Everything you need to know about the Deno 2 runtime

* * *

This feature is in Public Alpha. [Submit a support ticket](https://supabase.help) if you have any issues.

### What is Deno 2?[#](#what-is-deno-2)

Deno 2 is a major upgrade to the Deno runtime that powers Supabase Edge Functions. It focuses on scalability and seamless ecosystem compatibility while maintaining Deno's core principles of security, simplicity, and developer experience.

**Key improvements include**

-   **Node.js and npm compatibility**: Dramatically improved support for npm packages and Node.js code
-   **Better dependency management**: New tools like `deno install`, `deno add`, and `deno remove` for simplified package management
-   **Improved performance**: Enhanced runtime execution and startup times
-   **Workspace and monorepo support**: Better handling of complex project structures
-   **Framework compatibility**: Support for Next.js, SvelteKit, Remix, and other popular frameworks
-   **Full package.json support**: Works seamlessly with existing Node.js projects and npm workspaces

While these improvements are exciting, they come with some changes that may affect your existing functions. We'll support Deno 1.x functions for a limited time, but we recommend migrating to Deno 2 within the next few months to ensure continued functionality.

### How to use Deno 2[#](#how-to-use-deno-2)

Deno 2 will soon become the default choice for creating new functions. For now, Deno 2 is available in preview mode for local development.

Here's how you can build and deploy a function with Deno 2:

-   [Install Deno 2.1](https://docs.deno.com/runtime/getting_started/installation/) or newer version on your machine
    
-   Go to your Supabase project. `cd my-supabase-project`
    
-   Open `supabase/config.toml` and set `deno_version = 2`
    

```
12[edge_runtime]deno_version = 2
```

-   All your existing functions should work as before.

To scaffold a new function as a Deno 2 project:

```
1deno init --serve hello-world
```

-   Open `supabase/config.toml` and add the following:

```
12[functions.hello-world]entrypoint = "./functions/hello-world/main.ts"
```

-   Open supabase/functions/hello-world/main.ts and modify line 10 to:

```
1if (url.pathname === "/hello-world") {
```

-   Use `npx supabase@beta functions serve --no-verify-jwt` to start the dev server.
    
-   Visit [http://localhost:54321/functions/v1/hello-world](http://localhost:54321/functions/v1/hello-world).
    
-   To run built-in tests, `cd supabase/functions/hello-world; deno test`
    

### How to migrate existing functions from Deno 1 to Deno 2[#](#how-to-migrate-existing-functions-from-deno-1-to-deno-2)

For a comprehensive migration guide, see the [official Deno 1.x to 2.x migration guide](https://docs.deno.com/runtime/reference/migration_guide/#content).

Most Deno 1 Edge Functions will be compatible out of the box with Deno 2, and no action needs to be taken. When we upgrade our hosted runtime, your functions will automatically be deployed on a Deno 2 cluster.

However, for a small number of functions, this may break existing functionality.

The most common issue to watch for is that some Deno 1 API calls are incompatible with Deno 2 runtime.

For instance if you are using:

-   `Deno.Closer`

Use [`Closer`](https://jsr.io/@std/io/doc/types/~/Closer) from the Standard Library instead.

```
12345+ import type { Closer } from "jsr:@std/io/types";- function foo(closer: Deno.Closer) {+ function foo(closer: Closer) {  // ...}
```

The best way to validate your APIs are up to date is to use the Deno lint, which has [rules to disallow deprecated APIs](https://docs.deno.com/lint/rules/no-deprecated-deno-api/).

```
1deno lint
```

For a full list of API changes, see the [official Deno 2 list](https://docs.deno.com/runtime/reference/migration_guide/#api-changes).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/deno2.mdx)

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