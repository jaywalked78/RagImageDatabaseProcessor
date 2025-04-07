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

3.  Debugging

5.  [Local Debugging with DevTools](https://supabase.com/docs/guides/functions/debugging-tools)

# 

Local Debugging with DevTools

## 

How to use Chrome DevTools to debug Edge Functions.

* * *

Since [v1.171.0](https://github.com/supabase/cli/releases/tag/v1.171.0) the Supabase CLI supports debugging Edge Functions via the v8 inspector protocol, allowing for debugging via [Chrome DevTools](https://developer.chrome.com/docs/devtools/) and other Chromium-based browsers.

### Inspect with Chrome Developer Tools[#](#inspect-with-chrome-developer-tools)

You can use the [Chrome DevTools](https://developer.chrome.com/docs/devtools/) to set breakpoints and inspect the execution of your Edge Functions.

1.  Serve your functions in [inspect mode](https://supabase.com/docs/reference/cli/supabase-functions-serve): `supabase functions serve --inspect-mode brk`. This will set a breakpoint at the first line to pause script execution before any code runs.
2.  In your Chrome browser navigate to `chrome://inspect`.
3.  Click the "Configure..."" button to the right of the Discover network targets checkbox.
4.  In the Target discovery settings dialog box that opens, enter `127.0.0.1:8083` in the blank space and click the "Done" button to exit the dialog box.
5.  Click "Open dedicated DevTools for Node" to complete the preparation for debugging. The opened DevTools window will now listen to any incoming requests to edge-runtime.
6.  Send a request to your function running locally, e.g. via curl or Postman. The DevTools window will now pause script execution at first line.
7.  In the "Sources" tab navigate to `file://` > `home/deno/functions/<your-function-name>/index.ts`.
8.  Use the DevTools to set breakpoints and inspect the execution of your Edge Function.

![Debugging in Chrome DevTools.](https://supabase.com/docs/img/guides/functions/debug-chrome-devtools.png)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/debugging-tools.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FsOrtcoKg5zQ%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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