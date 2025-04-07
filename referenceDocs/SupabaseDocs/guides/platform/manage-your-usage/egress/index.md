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

7.  [Egress](https://supabase.com/docs/guides/platform/manage-your-usage/egress)

# 

Manage Egress usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the network data transmitted out of the system to a connected client. Egress is incurred by all services - Database, Auth, Storage, Edge Functions, Realtime and Log Drains.

### Database Egress[#](#database-egress)

Data sent to the client when retrieving data stored in your database.

**Example:** A user views their order history in an online shop. The client application requests the database to retrieve the user's past orders. The order data is sent back to the client, contributing to Database Egress.

There are various ways to interact with your database, such as through the PostgREST API using one of the client SDKs or via the Supavisor connection pooler. On the Supabase Dashboard, Egress from the PostgREST API is labeled as **Database Egress**, while Egress through Supavisor is labeled as **Supavisor Egress**.

### Auth Egress[#](#auth-egress)

Data sent from Supabase Auth to the client while managing your application's users. This includes actions like signing in, signing out, or creating new users, e.g. via the JavaScript Client SDK.

**Example:** A user signs in to an online shop. The client application requests the Supabase Auth service to authenticate and authorize the user. The session data, including authentication tokens and user profile details, is sent back to the client, contributing to Auth Egress.

### Storage Egress[#](#storage-egress)

Data sent from Supabase Storage to the client when retrieving assets. This includes actions like downloading files, images, or other stored content, e.g. via the JavaScript Client SDK.

**Example:** A user downloads an invoice from an online shop. The client application requests Supabase Storage to retrieve the PDF file from the storage bucket. The file is sent back to the client, contributing to Storage Egress.

### Edge Functions Egress[#](#edge-functions-egress)

Data sent to the client when executing Edge Functions.

**Example:** A user completes a checkout process in an online shop. The client application triggers an Edge Function to process the payment and confirm the order. The confirmation response, along with any necessary details, is sent back to the client, contributing to Edge Functions Egress.

### Realtime Egress[#](#realtime-egress)

Data pushed to clients via Supabase Realtime for subscribed events.

**Example:** When a user views a product page in an online shop, their client subscribes to real-time inventory updates. As stock levels change, Supabase Realtime pushes updates to all subscribed clients, contributing to Realtime Egress.

### Log Drain Egress[#](#log-drain-egress)

Data pushed to the connected log drain.

**Example:** You set up a log drain, each log sent to the log drain is considered egress. You can toggle the GZIP option to reduce egress, in case your provider supports it.

## How charges are calculated[#](#how-charges-are-calculated)

Egress is charged by gigabyte. Charges apply only for usage exceeding your subscription plan's quota. This quota is called the Unified Egress Quota because it can be used across all services (Database, Auth, Storage etc.).

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Egress GB" on your invoice.

## Pricing[#](#pricing)

$0.09 per GB per month. You are only charged for usage exceeding your subscription plan's quota.

| Plan | Unified Egress Quota | Over-Usage per month |
| --- | --- | --- |
| Free | 5 GB | \- |
| Pro | 250 GB | $0.09 per GB |
| Team | 250 GB | $0.09 per GB |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's Egress usage is within the quota, so no charges for Egress apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Egress | 200 GB | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's Egress usage exceeds the quota by 50 GB, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Egress | 300 GB | $4.5 |
| **Subtotal** |  | **$39.5** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$29.5** |

## View usage[#](#view-usage)

### Usage page[#](#usage-page)

You can view Egress usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Total Egress section, you can see the usage for the selected time period. Hover over a specific date to view a breakdown by service.

### Custom report[#](#custom-report)

1.  On the [reports page](https://supabase.com/dashboard/project/_/reports), click **New custom report** in the left navigation menu
2.  After creating a new report, add charts for one or more Supabase services by clicking **Add block**

## Debug usage[#](#debug-usage)

To better understand your Egress usage, identify what’s driving the most traffic. Check the most frequent database queries, or analyze the most requested API paths to pinpoint high-bandwidth endpoints.

### Frequent database queries[#](#frequent-database-queries)

On the Advisors [Query performance view](https://supabase.com/dashboard/project/_/database/query-performance?preset=most_frequent&sort=calls&order=desc) you can see the most frequent queries and the average number of rows returned.

### Most requested API endpoints[#](#most-requested-api-endpoints)

In the [Logs Explorer](https://supabase.com/dashboard/project/_/logs/explorer) you can access Edge Logs, and review the top paths to identify heavily queried endpoints. These logs currently do not include response byte data. That data will be available in the future too.

## Optimize usage[#](#optimize-usage)

-   Reduce the number of fields or entries selected when querying your database
-   Reduce the number of queries or calls by optimizing client code or using caches
-   For update or insert queries, configure your ORM or queries to not return the entire row if not needed
-   When running manual backups through Supavisor, remove unneeded tables and/or reduce the frequency
-   Refer to the [Storage Optimizations guide](https://supabase.com/docs/guides/storage/production/scaling#egress) for tips on reducing Storage Egress

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/egress.mdx)

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