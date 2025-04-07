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

# Check usage for monthly active users (MAU)

Last edited: 1/17/2025

* * *

You can see the usage in your [projects usage page](https://app.supabase.com/project/_/settings/billing/usage).

For MAU, we rely on the [Auth Server](https://github.com/supabase/auth) logs. MAU count is relative to your billing cycle and resets whenever your billing cycle resets. You can check your Auth logs in your [projects logs & analytics section](https://supabase.com/dashboard/project/_/logs/auth-logs).

We do a distinct count of all user ids in the billing cycle. An Auth event can be a login, token refresh, logout, ... If an authenticated user does any of this, we count it towards the MAU. A user is only counted once towards MAU in a billing cycle.

The log retention for you as a user (accessible time) depends on your plan. Free plan users can access the logs of the last day, Pro plan users 7 days, Team plan users 28 days, Enterprise users 90 days. Unless you're on an Enterprise plan, you won't be able to execute the query to determine MAU yourself, as you don't have access to the logs in the past 30ish days (depending on your billing cycle).

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[MAU](https://supabase.com/docs/guides/troubleshooting?tags=MAU)[Monthly active users](https://supabase.com/docs/guides/troubleshooting?tags=Monthly+active+users)

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