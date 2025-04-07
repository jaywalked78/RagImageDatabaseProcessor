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

7.  [Realtime Messages](https://supabase.com/docs/guides/platform/manage-your-usage/realtime-messages)

# 

Manage Realtime Messages usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the number of messages going through Supabase Realtime throughout the billing cycle. Includes database changes, Broadcast and Presence.

**Database changes** Each database change counts as one message per client that listens to the event. For example, if a database change occurs and 5 clients listen to that database event, it counts as 5 messages.

**Broadcast** Each broadcast message counts as one message sent plus one message per subscribed client that receives it. For example, if you broadcast a message and 4 clients listen to it, it counts as 5 messages—1 sent and 4 received.

## How charges are calculated[#](#how-charges-are-calculated)

Realtime Messages are billed using Package pricing, with each package representing 1 million messages. If your usage falls between two packages, you are billed for the next whole package.

### Example[#](#example)

For simplicity, let's assume a package size of 1,000,000 and a charge of $2.50 per package without quota.

| Messages | Packages Billed | Costs |
| --- | --- | --- |
| 999,999 | 1 | $2.50 |
| 1,000,000 | 1 | $2.50 |
| 1,000,001 | 2 | $5.00 |
| 1,500,000 | 2 | $5.00 |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Realtime Messages" on your invoice.

## Pricing[#](#pricing)

$2.50 per 1 million messages. You are only charged for usage exceeding your subscription plan's quota.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Free | 2 million | \- |
| Pro | 5 million | $2.50 per 1 million messages |
| Team | 5 million | $2.50 per 1 million messages |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's Realtime messages are within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Realtime Messages | 1.8 million messages | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's Realtime messages exceed the quota by 3.5 million, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Realtime Messages | 8.5 million messages | $10 |
| **Subtotal** |  | **$45** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$35** |

## View usage[#](#view-usage)

You can view Realtime Messages usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Realtime Messages section, you can see the usage for the selected time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/realtime-messages.mdx)

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