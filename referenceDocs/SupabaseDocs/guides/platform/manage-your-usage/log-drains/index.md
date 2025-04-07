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

7.  [Log Drains](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains)

# 

Manage Log Drain usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You can configure log drains in the [project settings](https://supabase.com/dashboard/project/_/settings/log-drains) to send logs to one or more destinations. You are charged for each log drain that is configured (referred to as [Log Drain Hours](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains#log-drain-hours)), the log events sent (referred to as [Log Drain Events](https://supabase.com/docs/guides/platform/manage-your-usage/log-drains#log-drain-events)), and the [Egress](https://supabase.com/docs/guides/platform/manage-your-usage/egress) incurred by the export—across all your projects.

## Log Drain Hours[#](#log-drain-hours)

### How charges are calculated[#](#how-charges-are-calculated)

You are charged by the hour, meaning you are charged for the exact number of hours that a log drain is configured for a project. If a log drain is configured for part of an hour, you are still charged for the full hour.

#### Example[#](#example)

Your billing cycle runs from January 1 to January 31. On January 10 at 4:30 PM, you configure a log drain for your project. At the end of the billing cycle you are billed for 512 hours.

| Time Window | Log Drain Configured | Hours Billed | Description |
| --- | --- | --- | --- |
| January 1, 00:00 AM - January 10, 4:00 PM | No | 0 |  |
| January 10, 04:00 PM - January 10, 4:30 PM | No | 0 |  |
| January 10, 04:30 PM - January 10, 5:00 PM | Yes | 1 | full hour is billed |
| January 10, 05:00 PM - January 31, 23:59 PM | Yes | 511 |  |

#### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Log Drain Hours" on your invoice.

### Pricing[#](#pricing)

Log Drains are available as a project Add-On for all Team and Enterprise users. Each Log Drain costs $0.0822 per hour ($60 per month).

## Log Drain Events[#](#log-drain-events)

### How charges are calculated[#](#how-charges-are-calculated)

Log Drain Events are billed using Package pricing, with each package representing 1 million events. If your usage falls between two packages, you are billed for the next whole package.

#### Example[#](#example)

| Events | Packages Billed | Costs |
| --- | --- | --- |
| 999,999 | 1 | $0.2 |
| 1,000,000 | 1 | $0.2 |
| 1,000,001 | 2 | $0.4 |
| 1,500,000 | 2 | $0.4 |

#### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Log Drain Events" on your invoice.

### Pricing[#](#pricing)

$0.2 per 1 million events.

## Billing example[#](#billing-example)

The project has two log drains configured throughout the entire billing cycle with 800,000 and 1.6 million events each. In this example we assume that the organization is exceeding its Unified Egress Quota, so charges for Egress apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Team Plan | 1 | $599 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 hours | $10 |
|  |  |  |
| Log Drain Hours Drain 1 | 744 hours | $60 |
| Log Drain Events Drain 1 | 800,000 events | $0.2 |
| Egress Drain 1 | 2 GB | $0.18 |
|  |  |  |
| Log Drain Hours Drain 2 | 744 hours | $60 |
| Log Drain Events Drain 2 | 1.6 million events | $0.4 |
| Egress Drain 2 | 4 GB | $0.36 |
|  |  |  |
| **Subtotal** |  | **$730.14** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$720.14** |

## View usage[#](#view-usage)

You can view Log Drain Events usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/log-drains.mdx)

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