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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  More

5.  [Manage your usage](https://supabase.com/docs/guides/platform/manage-your-usage)

7.  [Realtime Peak Connections](https://supabase.com/docs/guides/platform/manage-your-usage/realtime-peak-connections)

# 

Manage Realtime Peak Connections usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

Realtime Peak Connections are measured by tracking the highest number of concurrent connections for each project during the billing cycle. Regardless of fluctuations, only the peak count per project is used for billing, and the totals from all projects are summed. Only successful connections are counted, connection attempts are not included.

### Example[#](#example)

For simplicity, this example assumes a billing cycle of only three days.

| Project | Peak Connections Day 1 | Peak Connections Day 2 | Peak Connections Day 3 |
| --- | --- | --- | --- |
| Project A | 80 | 100 | 90 |
| Project B | 120 | 110 | 150 |

**Total billed connections:** 100 (Project A) + 150 (Project B) = **250 connections**

## How charges are calculated[#](#how-charges-are-calculated)

Realtime Peak Connections are billed using Package pricing, with each package representing 1,000 peak connections. If your usage falls between two packages, you are billed for the next whole package.

### Example[#](#example)

For simplicity, let's assume a package size of 1,000 and a charge of $10 per package with no quota.

| Peak Connections | Packages Billed | Costs |
| --- | --- | --- |
| 999 | 1 | $10 |
| 1,000 | 1 | $10 |
| 1,001 | 2 | $20 |
| 1,500 | 2 | $20 |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Realtime Peak Connections" on your invoice.

## Pricing[#](#pricing)

$10 per 1,000 peak connections. You are only charged for usage exceeding your subscription plan's quota.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Free | 200 | \- |
| Pro | 500 | $10 per 1,000 peak connections |
| Team | 500 | $10 per 1,000 peak connections |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's connections are within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Realtime Peak Connections | 350 connections | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's connections exceed the quota by 1,200, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Realtime Peak Connections | 1,700 connections | $20 |
| **Subtotal** |  | **$45** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$35** |

## View usage[#](#view-usage)

You can view Realtime Peak Connections usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Realtime Peak Connections section, you can see the usage for the selected time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/realtime-peak-connections.mdx)

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