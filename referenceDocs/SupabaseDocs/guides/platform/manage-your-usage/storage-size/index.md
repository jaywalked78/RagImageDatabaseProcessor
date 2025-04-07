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

7.  [Storage Size](https://supabase.com/docs/guides/platform/manage-your-usage/storage-size)

# 

Manage Storage size usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the total size of all assets in your buckets.

## How charges are calculated[#](#how-charges-are-calculated)

Storage size is charged by Gigabyte-Hours (GB-Hrs). 1 GB-Hr represents the use of 1 GB of storage for 1 hour. For example, storing 10 GB of data for 5 hours results in 50 GB-Hrs (10 GB × 5 hours).

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Storage Size GB-Hrs" on your invoice.

## Pricing[#](#pricing)

$0.00002919 per GB-Hr ($0.021 per GB per month). You are only charged for usage exceeding your subscription plan's quota.

| Plan | Quota in GB | Over-Usage per GB | Quota in GB-Hrs | Over-Usage per GB-Hr |
| --- | --- | --- | --- | --- |
| Free | 1 | \- | 744 | \- |
| Pro | 100 | $0.021 | 74,400 | $0.00002919 |
| Team | 100 | $0.021 | 74,400 | $0.00002919 |
| Enterprise | Custom | Custom | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's Storage size usage is within the quota, so no charges for Storage size apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Storage Size | 85 GB | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's Storage size usage exceeds the quota by 257 GB, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Storage Size | 357 GB | $5.4 |
| **Subtotal** |  | **$40.4** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$30.4** |

## View usage[#](#view-usage)

### Usage page[#](#usage-page)

You can view Storage size usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Storage size section, you can see how much storage your projects have used during the selected time period.

### SQL Editor[#](#sql-editor)

Since we designed Storage to work as an integrated part of your Postgres database on Supabase, you can query information about your Storage objects in the `storage` schema.

List files larger than 5 MB:

```
123456789101112131415161718select    name,    bucket_id as bucket,    case        when (metadata->>'size')::int >= 1073741824 then            ((metadata->>'size')::int / 1073741824.0)::numeric(10, 2) || ' GB'        when (metadata->>'size')::int >= 1048576 then            ((metadata->>'size')::int / 1048576.0)::numeric(10, 2) || ' MB'        when (metadata->>'size')::int >= 1024 then            ((metadata->>'size')::int / 1024.0)::numeric(10, 2) || ' KB'        else            (metadata->>'size')::int || ' bytes'        end as sizefrom    storage.objectswhere    (metadata->>'size')::int > 1048576 * 5order by (metadata->>'size')::int desc
```

List buckets with their total size:

```
123456789select    bucket_id,    (sum((metadata->>'size')::int) / 1048576.0)::numeric(10, 2) as total_size_megabytefrom    storage.objectsgroup by    bucket_idorder by    total_size_megabyte desc;
```

## Optimize usage[#](#optimize-usage)

-   [Limit the upload size](https://supabase.com/docs/guides/storage/production/scaling#limit-the-upload-size) for your buckets
-   [Delete assets](https://supabase.com/docs/guides/storage/management/delete-objects) that are no longer in use

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/storage-size.mdx)

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