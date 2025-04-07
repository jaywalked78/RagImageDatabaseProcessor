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

7.  [Branching](https://supabase.com/docs/guides/platform/manage-your-usage/branching)

# 

Manage Branching usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

Each [Preview branch](https://supabase.com/docs/guides/deployment/branching) is a separate environment with all Supabase services (Database, Auth, Storage, etc.). You're charged for usage within that environment—such as [Compute](https://supabase.com/docs/guides/platform/manage-your-usage/compute), [Disk Size](https://supabase.com/docs/guides/platform/manage-your-usage/disk-size), [Egress](https://supabase.com/docs/guides/platform/manage-your-usage/egress), and [Storage](https://supabase.com/docs/guides/platform/manage-your-usage/storage-size)—just like the project you branched from.

Usage by Preview branches counts toward your subscription plan's quota.

## How charges are calculated[#](#how-charges-are-calculated)

Refer to individual [usage items](https://supabase.com/docs/guides/platform/manage-your-usage) for details on how charges are calculated. Branching charges are the sum of all these items.

### Usage on your invoice[#](#usage-on-your-invoice)

Compute incurred by Preview branches is shown as "Branching Compute Hours" on your invoice. Other usage items are not shown separately for branches and are rolled up into the project.

## Pricing[#](#pricing)

There is no fixed fee for a Preview branch. You only pay for the usage it incurs. With Compute costs of $0.01344 per hour, a branch running on Micro Compute size starts at $0.32 per day.

## Billing examples[#](#billing-examples)

The project has a Preview branch "XYZ", that runs for 30 hours, incurring Compute and Egress costs. Disk Size usage remains within the 8 GB included in the subscription plan, so no additional charges apply.

| Line Item | Costs |
| --- | --- |
| Pro Plan | $25 |
|  |  |
| Compute Hours Small Project 1 | $15 |
| Egress Project 1 | $7 |
| Disk Size Project 1 | $3 |
|  |  |
| Compute Hours Micro Branch XYZ | $0.4 |
| Egress Branch XYZ | $1 |
| Disk Size Branch XYZ | $0 |
|  |  |
| **Subtotal** | **$51.4** |
| Compute Credits | \-$10 |
| **Total** | **$41.4** |

## View usage[#](#view-usage)

You can view Branching usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Usage Summary section, you can see how many hours your Preview branches existed during the selected time period. Hover over "Branches Compute Hours" for a detailed breakdown.

## Optimize usage[#](#optimize-usage)

-   Merge Preview branches as soon as they are ready
-   Delete Preview branches that are no longer in use
-   Check whether your [persistent branches](https://supabase.com/docs/guides/deployment/branching#persistent-branches) need to be defined as persistent, or if they can be ephemeral instead. Persistent branches will remain active even after the underlying PR is closed.

## FAQ[#](#faq)

### Do Compute Credits apply to Branching Compute?[#](#do-compute-credits-apply-to-branching-compute)

No, Compute Credits do not apply to Branching Compute.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/branching.mdx)

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