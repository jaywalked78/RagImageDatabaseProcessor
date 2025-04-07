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

7.  [Edge Function Invocations](https://supabase.com/docs/guides/platform/manage-your-usage/edge-function-invocations)

# 

Manage Edge Function Invocations usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the number of times your functions get invoked, regardless of the response status code.

## How charges are calculated[#](#how-charges-are-calculated)

Edge Function Invocations are billed using Package pricing, with each package representing 1 million invocations. If your usage falls between two packages, you are billed for the next whole package.

### Example[#](#example)

For simplicity, let's assume a package size of 1 million and a charge of $2 per package without a free quota.

| Invocations | Packages Billed | Costs |
| --- | --- | --- |
| 999,999 | 1 | $2 |
| 1,000,000 | 1 | $2 |
| 1,000,001 | 2 | $4 |
| 1,500,000 | 2 | $4 |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Function Invocations" on your invoice.

## Pricing[#](#pricing)

$2 per 1 million invocations. You are only charged for usage exceeding your subscription plan's quota.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Free | 500,000 | \- |
| Pro | 2 million | $2 per 1 million invocations |
| Team | 2 million | $2 per 1 million invocations |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's function invocations are within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Function Invocations | 1,800,000 invocations | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's function invocations exceed the quota by 1.4 million, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Function Invocations | 3,400,000 invocations | $4 |
| **Subtotal** |  | **$39** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$29** |

## View usage[#](#view-usage)

You can view Edge Function Invocations usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Edge Function Invocations section, you can see how many invocations your projects have had during the selected time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/edge-function-invocations.mdx)

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