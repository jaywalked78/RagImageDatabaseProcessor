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

7.  [Migrating from Auth Helpers](https://supabase.com/docs/guides/auth/server-side/migrating-to-ssr-from-auth-helpers)

# 

Migrating to the SSR package from Auth Helpers

* * *

The new `ssr` package takes the core concepts of the Auth Helpers and makes them available to any server language or framework. This page will guide you through migrating from the Auth Helpers package to `ssr`.

### Replacing Supabase packages[#](#replacing-supabase-packages)

Next.jsSvelteKitRemix

```
1npm uninstall @supabase/auth-helpers-nextjs
```

```
1npm install @supabase/ssr
```

### Creating a client[#](#creating-a-client)

The new `ssr` package exports two functions for creating a Supabase client. The `createBrowserClient` function is used in the client, and the `createServerClient` function is used in the server.

Check out the [Creating a client](https://supabase.com/docs/guides/auth/server-side/creating-a-client) page for examples of creating a client in your framework.

## Next steps[#](#next-steps)

-   Implement [Authentication using Email and Password](https://supabase.com/docs/guides/auth/server-side/email-based-auth-with-pkce-flow-for-ssr)
-   Implement [Authentication using OAuth](https://supabase.com/docs/guides/auth/server-side/oauth-with-pkce-flow-for-ssr)
-   [Learn more about SSR](https://supabase.com/docs/guides/auth/server-side-rendering)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/server-side/migrating-to-ssr-from-auth-helpers.mdx)

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