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

7.  [Disk Size](https://supabase.com/docs/guides/platform/manage-your-usage/disk-size)

# 

Manage Disk size usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

Each database has a dedicated [disk](https://supabase.com/docs/guides/platform/compute-and-disk#disk). You are charged for the provisioned disk size.

Disk size is not relevant for the Free Plan. Instead Free Plan customers are limited by [Database size](https://supabase.com/docs/guides/platform/database-size).

## How charges are calculated[#](#how-charges-are-calculated)

Disk size is charged by Gigabyte-Hours (GB-Hrs). 1 GB-Hr represents 1 GB being provisioned for 1 hour. For example, having 10 GB provisioned for 5 hours results in 50 GB-Hrs (10 GB × 5 hours).

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Disk Size GB-Hrs" on your invoice.

## Pricing[#](#pricing)

Pricing depends on the [disk type](https://supabase.com/docs/guides/platform/compute-and-disk#disk-types), with gp3 being the default disk type.

### General purpose disks (gp3)[#](#general-purpose-disks-gp3)

$0.000171 per GB-Hr ($0.125 per GB per month). The primary database of your project gets provisioned with an 8 GB disk. You are only charged for provisioned disk size exceeding these 8 GB.

| Plan | Included Disk Size | Over-Usage per GB per month | Over-Usage per GB-Hr |
| --- | --- | --- | --- |
| Pro | 8 GB | $0.125 | $0.000171 |
| Team | 8 GB | $0.125 | $0.000171 |
| Enterprise | Custom | Custom | Custom |

Launching a Read Replica creates an additional database with its own dedicated disk. You are charged from the first byte of provisioned disk for the Read Replica. Refer to [Manage Read Replica usage](https://supabase.com/docs/guides/platform/manage-your-usage/read-replicas) for details on billing.

### High performance disks (io2)[#](#high-performance-disks-io2)

$0.000267 per GB-Hr ($0.195 per GB per month). Unlike general purpose disks, high performance disks are billed from the first byte of provisioned disk.

| Plan | Included Disk size | Usage per GB per month | Usage per GB-Hr |
| --- | --- | --- | --- |
| Pro | 0 GB | $0.195 | $0.000267 |
| Team | 0 GB | $0.195 | $0.000267 |
| Enterprise | Custom | Custom | Custom |

## Billing examples[#](#billing-examples)

### Gp3[#](#gp3)

Project 1 and 2 don't exceed the included disk size, so no charges for Disk size apply. Project 3 exceeds the included disk size by 42 GB, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 hours | $10 |
| Disk Size Project 1 | 8 GB | $0 |
|  |  |  |
| Compute Hours Micro Project 2 | 744 hours | $10 |
| Disk Size Project 2 | 8 GB | $0 |
|  |  |  |
| Compute Hours Micro Project 3 | 744 hours | $10 |
| Disk Size Project 3 | 50 GB | $5.25 |
|  |  |  |
| **Subtotal** |  | **$50.25** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$40.25** |

### Io2[#](#io2)

This disk type is billed from the first byte of provisioned disk, meaning for 66 GB across all projects.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 hours | $10 |
| Disk Size Project 1 | 8 GB | $1.56 |
|  |  |  |
| Compute Hours Micro Project 2 | 744 hours | $10 |
| Disk Size Project 2 | 8 GB | $1.56 |
|  |  |  |
| Compute Hours Micro Project 3 | 744 hours | $10 |
| Disk Size Project 3 | 50 GB | $9.75 |
|  |  |  |
| **Subtotal** |  | **$67.87** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$57.87** |

## View usage[#](#view-usage)

You can view Disk size usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown.

In the Disk size section, you can see how much disk size your projects have provisioned.

### Disk size distribution[#](#disk-size-distribution)

To see how your disk usage is distributed across Database, WAL, and System categories, refer to [Disk size distribution](https://supabase.com/docs/guides/platform/database-size#disk-size-distribution).

## Reduce Disk size[#](#reduce-disk-size)

To see how you can downsize your disk, refer to [Reducing disk size](https://supabase.com/docs/guides/platform/database-size#reducing-disk-size)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/disk-size.mdx)

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