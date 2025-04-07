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

3.  Platform

5.  [Limits](https://supabase.com/docs/guides/functions/limits)

# 

Limits

## 

Limits applied Edge Functions in Supabase's hosted platform.

* * *

## Runtime limits[#](#runtime-limits)

-   Maximum Memory: 256MB
-   Maximum Duration (Wall clock limit): This is the duration an Edge Function worker will stay active. During this period, a worker can serve multiple requests or process background tasks.
    -   Free plan: 150s
    -   Paid plans: 400s
-   Maximum CPU Time: 2s (Amount of actual time spent on the CPU per request - does not include async I/O.)
-   Request idle timeout: 150s (If an Edge Function doesn't send a response before the timeout, 504 Gateway Timeout will be returned)
-   Maximum Function Size: 20MB (After bundling using CLI)
-   Maximum log message length: 10,000 characters
-   Log event threshold: 100 events per 10 seconds

## Other limits & restrictions[#](#other-limits--restrictions)

-   Outgoing connections to ports `25` and `587` are not allowed.
-   Serving of HTML content is only supported with [custom domains](https://supabase.com/docs/reference/cli/supabase-domains) (Otherwise `GET` requests that return `text/html` will be rewritten to `text/plain`).
-   Web Worker API (or Node `vm` API) are not available.
-   Node Libraries that require multithreading are not supported. Examples: [`libvips`](https://github.com/libvips/libvips), [sharp](https://github.com/lovell/sharp).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/limits.mdx)

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