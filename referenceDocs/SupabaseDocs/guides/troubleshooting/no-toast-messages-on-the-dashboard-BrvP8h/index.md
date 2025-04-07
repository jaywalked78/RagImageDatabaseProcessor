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

# No toast messages on the Dashboard

Last edited: 1/18/2025

* * *

This is a known issue that is on the roadmap to resolve. However, this discussion serves as a temporary workaround for affected users until then.

## What is the issue?[#](#what-is-the-issue)

When executing operations in the Supabase dashboard, there are situations where you will not see a toast message in the top right corner to indicate the status of the operation. This leaves users confused about the operation's status and why it errored. They would then have to look in the browser console logs for further details.

Here is an example of a toast error message:

![Screenshot 2024-07-01 at 2 05 36 PM](https://supabase.com/docs/img/troubleshooting/8ba54441-2057-4dc0-8add-a8eaab9f2d93.png)

Here is an example of a toast success message:

![Screenshot 2024-07-01 at 2 06 35 PM](https://supabase.com/docs/img/troubleshooting/c6e228b8-fa64-47a9-bdf6-f1f6405b9cf9.png)

## What causes it?[#](#what-causes-it)

If you are not seeing these error messages, there are a couple of known scenarios that might be blocking them:

1.  **Brave Browser**: By default, Brave has strict ad-blocking settings that can block these messages.
    
2.  **Chrome Browser**: Specifically, the ARM64 build (tested on v125.0.6422.142) with the new v3 manifest version of uBlock Origin Lite ([https://ublockorigin.com/](https://ublockorigin.com/)). If the setting is changed from basic to optimal, it can block these messages.
    

There are likely other causes that are not known right now as well.

## How to fix this issue?[#](#how-to-fix-this-issue)

**Adjust Ad-blocking Settings**: Turn down the ad-blocking settings or turn it off for the Supabase dashboard.

**Use a different Browser**: If the above is not feasible, using a different browser is an alternative.

## Metadata

* * *

### Products

[Studio](https://supabase.com/docs/guides/troubleshooting?products=studio)

* * *

### Tags

[notifications](https://supabase.com/docs/guides/troubleshooting?tags=notifications)[toasts](https://supabase.com/docs/guides/troubleshooting?tags=toasts)

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