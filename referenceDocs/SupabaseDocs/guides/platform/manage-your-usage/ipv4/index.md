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

7.  [IPv4](https://supabase.com/docs/guides/platform/manage-your-usage/ipv4)

# 

Manage IPv4 usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You can assign a dedicated [IPv4 address](https://supabase.com/docs/guides/platform/ipv4-address) to a database by enabling the [IPv4 add-on](https://supabase.com/dashboard/project/_/settings/addons?panel=ipv4). You are charged for all IPv4 addresses configured across your databases.

If the primary database has a dedicated IPv4 address configured, its Read Replicas are also assigned one, with charges for each.

## How charges are calculated[#](#how-charges-are-calculated)

IPv4 addresses are charged by the hour, meaning you are charged for the exact number of hours that an IPv4 address is assigned to a database. If an address is assigned for part of an hour, you are still charged for the full hour.

### Example[#](#example)

Your billing cycle runs from January 1 to January 31. On January 10 at 4:30 PM, you enable the IPv4 add-on for your project. At the end of the billing cycle you are billed for 512 hours.

| Time Window | IPv4 add-on | Hours Billed | Description |
| --- | --- | --- | --- |
| January 1, 00:00 AM - January 10, 4:00 PM | Disabled | 0 |  |
| January 10, 04:00 PM - January 10, 4:30 PM | Disabled | 0 |  |
| January 10, 04:30 PM - January 10, 5:00 PM | Enabled | 1 | full hour is billed |
| January 10, 05:00 PM - January 31, 23:59 PM | Enabled | 511 |  |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "IPv4 Hours" on your invoice.

## Pricing[#](#pricing)

$0.0055 per hour ($4 per month).

## Billing examples[#](#billing-examples)

### One project[#](#one-project)

The project has the IPv4 add-on enabled throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
| Compute Hours Micro Project 1 | 744 | $10 |
| IPv4 Hours | 744 | $4 |
| **Subtotal** |  | **$39** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$29** |

### Multiple projects[#](#multiple-projects)

All projects have the IPv4 add-on enabled throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 | $10 |
| IPv4 Hours Project 1 | 744 | $4 |
|  |  |  |
| Compute Hours Micro Project 2 | 744 | $10 |
| IPv4 Hours Project 2 | 744 | $4 |
|  |  |  |
| Compute Hours Micro Project 3 | 744 | $10 |
| IPv4 Hours Project 3 | 744 | $4 |
|  |  |  |
| **Subtotal** |  | **$67** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$57** |

### One project with Read Replicas[#](#one-project-with-read-replicas)

The project has two Read Replicas and the IPv4 add-on enabled throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
|  |  |  |
| Compute Hours Small Project 1 | 744 | $15 |
| IPv4 Hours Project 1 | 744 | $4 |
|  |  |  |
| Compute Hours Small Replica 1 | 744 | $15 |
| IPv4 Hours Replica 1 | 744 | $4 |
|  |  |  |
| Compute Hours Small Replica 2 | 744 | $15 |
| IPv4 Hours Replica 2 | 744 | $4 |
|  |  |  |
| **Subtotal** |  | **$82** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$72** |

## Optimize usage[#](#optimize-usage)

To see whether your database actually needs a dedicated IPv4 address, refer to [When you need the IPv4 add-on](https://supabase.com/docs/guides/platform/ipv4-address#when-you-need-the-ipv4-add-on).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/ipv4.mdx)

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