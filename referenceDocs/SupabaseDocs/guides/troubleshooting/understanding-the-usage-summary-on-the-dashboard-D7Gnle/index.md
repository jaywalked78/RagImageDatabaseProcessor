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

# Understanding the Usage Summary on the Dashboard

Last edited: 1/18/2025

* * *

## Organization usage metrics[#](#organization-usage-metrics)

This discussion explains your organization's usage metrics, which can be found here: [https://supabase.com/dashboard/org/\_/usage](https://supabase.com/dashboard/org/_/usage).

![](https://supabase.com/docs/img/troubleshooting/46f59019-6ff1-4bfb-9acd-d5b7bd282f89.png)

These metrics are calculated based on all the projects under the organization that meet these criteria:

-   Currently active projects
-   Inactive projects that were active for some period of time within the current billing cycle

This may be confusing for users looking at only what metrics are being used for currently active projects.

## Database size example[#](#database-size-example)

Using the database size as an example, suppose we have the following projects under the organization:

-   Project A: 1 GB database size
-   Project B: 0.5 GB database size
-   Project C: 0.5 GB database size

If the user decides to delete Projects A and B during the current billing cycle, the average database usage will be 2 GB for the current billing cycle, even though only a 0.5 GB database is currently active.

As of now, even if your project was just active for a few days, we take the average database size for those active days, which may lead to high usage when creating and deleting many projects within a billing cycle. We're working on a better billing model to cover these cases.

## Edge Functions example[#](#edge-functions-example)

Consider another example with edge functions. Suppose we have these projects under the organization:

-   Project D: 5 Edge Functions
-   Project E: 7 Edge Functions

If Project E with its 7 functions is deleted during the current billing cycle, the average Edge Function count for this billing cycle on the dashboard will still be 12 functions.

## Other metrics[#](#other-metrics)

It is a little more tricky to understand metrics like realtime and egress due to being more complex to track usage compared to Database size or Function count. However, they will account for usage from all projects that are active or were active during your current billing cycle as well.

## Metrics still look weird or incorrect?[#](#metrics-still-look-weird-or-incorrect)

If the numbers from inactive projects carry over to the next billing cycle and no new usage has occurred, something might be wrong.

If this is the case, or if you are unsure why any usage appears the way it does for any reason, you should reach out to Support on the dashboard here: [https://supabase.com/dashboard/support/new](https://supabase.com/dashboard/support/new).

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Studio](https://supabase.com/docs/guides/troubleshooting?products=studio)[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Functions](https://supabase.com/docs/guides/troubleshooting?products=functions)

* * *

### Tags

[usage](https://supabase.com/docs/guides/troubleshooting?tags=usage)[metrics](https://supabase.com/docs/guides/troubleshooting?tags=metrics)[projects](https://supabase.com/docs/guides/troubleshooting?tags=projects)

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