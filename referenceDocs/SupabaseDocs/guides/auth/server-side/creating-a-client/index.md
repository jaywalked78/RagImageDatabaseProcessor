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

Auth

1.  Auth

3.  More

5.  [Server-Side Rendering](https://supabase.com/docs/guides/auth/server-side)

7.  [Creating a client](https://supabase.com/docs/guides/auth/server-side/creating-a-client)

# 

Creating a Supabase client for SSR

## 

Configure your Supabase client to use cookies

* * *

To use Server-Side Rendering (SSR) with Supabase, you need to configure your Supabase client to use cookies. The `@supabase/ssr` package helps you do this for JavaScript/TypeScript applications.

## Install[#](#install)

Install the `@supabase/ssr` and `@supabase/supabase-js` packages:

npmyarnpnpm

```
1npm install @supabase/ssr @supabase/supabase-js
```

## Set environment variables[#](#set-environment-variables)

In your environment variables file, set your Supabase URL and Supabase Anon Key:

###### Project URL

Loading...

###### Anon key

Loading...

Next.jsSvelteKitAstroRemixExpressHono

```
12NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_urlNEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Create a client[#](#create-a-client)

You'll need some one-time setup code to configure your Supabase client to use cookies. Once your utility code is set up, you can use your new `createClient` utility functions to get a properly configured Supabase client.

Use the browser client in code that runs on the browser, and the server client in code that runs on the server.

Next.jsSvelteKitAstroRemixExpressHono

The following code samples are for App Router. For help with Pages Router, see the [Next.js Server-Side Auth guide](https://supabase.com/docs/guides/auth/server-side/nextjs?queryGroups=router&router=pages).

Client-sideServer-sideMiddleware

## Next steps[#](#next-steps)

-   Implement [Authentication using Email and Password](https://supabase.com/docs/guides/auth/server-side/email-based-auth-with-pkce-flow-for-ssr)
-   Implement [Authentication using OAuth](https://supabase.com/docs/guides/auth/server-side/oauth-with-pkce-flow-for-ssr)
-   [Learn more about SSR](https://supabase.com/docs/guides/auth/server-side-rendering)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/server-side/creating-a-client.mdx)

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