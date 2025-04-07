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

7.  [Monthly Active Third-Party Users](https://supabase.com/docs/guides/platform/manage-your-usage/monthly-active-users-third-party)

# 

Manage Monthly Active Third-Party Users usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the number of distinct users who log in or refresh their token during the billing cycle using a third-party authentication provider. Each unique user is counted only once per billing cycle, regardless of how many times they authenticate. These users are referred to as "Third-Party MAUs".

### Example[#](#example)

Your billing cycle runs from January 1 to January 31. Although User-1 was signed in multiple times, they are counted as a single SSO MAU for this billing cycle.

1

### User-1 signs in via Auth0 on January 3

The Third-Party MAU count increases from 0 to 1.

2

### User-1 signs out on January 4.

3

### User-1 signs in via Auth0 again on January 17

The Third-Party MAU count remains 1.

## How charges are calculated[#](#how-charges-are-calculated)

You are charged by Third-Party MAU.

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Monthly Active Third-Party Users" on your invoice.

## Pricing[#](#pricing)

$0.00325 per Third-Party MAU. You are only charged for usage exceeding your subscription plan's quota.

The count resets at the start of each billing cycle.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Free | 50,000 | \- |
| Pro | 100,000 | $0.00325 per Third-Party MAU |
| Team | 100,000 | $0.00325 per Third-Party MAU |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's Third-Party MAU usage for the billing cycle is within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Monthly Active Third-Party Users | 37,000 Third-Party MAU | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's Third-Party MAU usage for the billing cycle exceeds the quota by 4950, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Monthly Active Third-Party Users | 130,000 Third-Party MAU | $97.50 |
| **Subtotal** |  | **$132.50** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$122.50** |

## View usage[#](#view-usage)

You can view Monthly Active Third-Party Users usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/monthly-active-users-third-party.mdx)

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