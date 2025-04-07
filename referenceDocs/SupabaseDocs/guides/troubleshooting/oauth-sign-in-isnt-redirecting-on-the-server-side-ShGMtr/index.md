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

# OAuth sign in isn't redirecting on the server side

Last edited: 2/4/2025

* * *

The reason behind this limitation is that the auth helpers library lacks a direct mechanism for performing server-side redirects, as each framework handles redirects differently. However, the library does offer a URL through the data property it returns, which should be utilized for the purpose of redirection.

**Next.js:**

```
1234567import { NextResponse } from "next/server";...const { data } = await supabase.auth.signInWithOAuth({  provider: 'github',})return NextResponse.redirect(data.url)
```

**SvelteKit:**

```
1234567import { redirect } from '@sveltejs/kit';...const { data } = await supabase.auth.signInWithOAuth({  provider: 'github',})throw redirect(303, data.url)
```

**Remix:**

```
1234567import { redirect } from "@remix-run/node"; // or cloudflare/deno...const { data } = await supabase.auth.signInWithOAuth({  provider: 'github',})return redirect(data.url)
```

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Tags

[oauth](https://supabase.com/docs/guides/troubleshooting?tags=oauth)[redirects](https://supabase.com/docs/guides/troubleshooting?tags=redirects)[server-side](https://supabase.com/docs/guides/troubleshooting?tags=server-side)

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