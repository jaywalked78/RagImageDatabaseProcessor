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

7.  [Custom Domains](https://supabase.com/docs/guides/platform/manage-your-usage/custom-domains)

# 

Manage Custom Domain usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You can configure a [custom domain](https://supabase.com/docs/guides/platform/custom-domains) for a project by enabling the [Custom Domain add-on](https://supabase.com/dashboard/project/_/settings/addons?panel=customDomain). You are charged for all custom domains configured across your projects.

## How charges are calculated[#](#how-charges-are-calculated)

Custom domains are charged by the hour, meaning you are charged for the exact number of hours that a custom domain is active. If a custom domain is active for part of an hour, you are still charged for the full hour.

### Example[#](#example)

Your billing cycle runs from January 1 to January 31. On January 10 at 4:30 PM, you activate a custom domain for your project. At the end of the billing cycle you are billed for 512 hours.

| Time Window | Custom Domain Activated | Hours Billed | Description |
| --- | --- | --- | --- |
| January 1, 00:00 AM - January 10, 4:00 PM | No | 0 |  |
| January 10, 04:00 PM - January 10, 4:30 PM | No | 0 |  |
| January 10, 04:30 PM - January 10, 5:00 PM | Yes | 1 | full hour is billed |
| January 10, 05:00 PM - January 31, 23:59 PM | Yes | 511 |  |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Custom Domain Hours" on your invoice.

## Pricing[#](#pricing)

$0.0137 per hour ($10 per month).

## Billing examples[#](#billing-examples)

### One project[#](#one-project)

The project has a custom domain activated throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
| Compute Hours Micro Project 1 | 744 | $10 |
| Custom Domain Hours | 744 | $10 |
| **Subtotal** |  | **$45** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$35** |

### Multiple projects[#](#multiple-projects)

All projects have a custom domain activated throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 | $10 |
| Custom Domain Hours Project 1 | 744 | $10 |
|  |  |  |
| Compute Hours Micro Project 2 | 744 | $10 |
| Custom Domain Hours Project 2 | 744 | $10 |
|  |  |  |
| **Subtotal** |  | **$65** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$55** |

## Optimize usage[#](#optimize-usage)

-   Regularly check your projects and remove custom domains that are no longer needed
-   Use free [Vanity subdomains](https://supabase.com/docs/guides/platform/custom-domains#vanity-subdomains) where applicable

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/custom-domains.mdx)

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