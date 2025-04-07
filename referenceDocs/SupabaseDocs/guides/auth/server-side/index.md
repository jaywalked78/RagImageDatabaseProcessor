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

3.  Flows (How-tos)

5.  [Server-Side Rendering](https://supabase.com/docs/guides/auth/server-side)

# 

Server-Side Rendering

## 

How SSR works with Supabase Auth.

* * *

SSR frameworks move rendering and data fetches to the server, to reduce client bundle size and execution time.

Supabase Auth is fully compatible with SSR. You need to make a few changes to the configuration of your Supabase client, to store the user session in cookies instead of local storage. After setting up your Supabase client, follow the instructions for any flow in the How-To guides.

Make sure to use the PKCE flow instructions where those differ from the implicit flow instructions. If no difference is mentioned, don't worry about this.

## `@supabase/ssr`[#](#supabasessr)

We have developed an [`@supabase/ssr`](https://www.npmjs.com/package/@supabase/ssr) package to make setting up the Supabase client as simple as possible. This package is currently in beta. Adoption is recommended but be aware that the API is still unstable and may have breaking changes in the future.

If you're currently using the [Auth Helpers package](https://github.com/supabase/auth-helpers), the [docs are still available](https://supabase.com/docs/guides/auth/auth-helpers), however we recommend migrating to the new `@supabase/ssr` package as this will be the recommended path moving forward.

## Framework quickstarts[#](#framework-quickstarts)

[

![Next.js](https://supabase.com/docs/img/icons/nextjs-icon.svg)

Next.js

Automatically configure Supabase in Next.js to use cookies, making your user and their session available on the client and server.



](https://supabase.com/docs/guides/auth/server-side/nextjs)[

![SvelteKit](https://supabase.com/docs/img/icons/svelte-icon.svg)

SvelteKit

Automatically configure Supabase in SvelteKit to use cookies, making your user and their session available on the client and server.



](https://supabase.com/docs/guides/auth/server-side/sveltekit)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/server-side.mdx)

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