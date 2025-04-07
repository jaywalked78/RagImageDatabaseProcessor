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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# All about Supabase Egress

Last edited: 2/12/2025

* * *

**What is Egress?**

Egress (also known as bandwidth) is any amount of network packets/bytes being streamed back to a connected client. Means, the data that is leaving the Supabase platform. Egress in Supabase includes any calls through PostgREST, to Storage, Realtime, Auth, Edge Functions, Database and Supavisor.

You can read about Unified egress, included quota, and how to check the egress usage here: [https://supabase.com/docs/guides/platform/manage-your-usage/egress](https://supabase.com/docs/guides/platform/manage-your-usage/egress). Additionally, the [project reports](https://supabase.com/dashboard/project/_/reports) have a few egress related stats. You can create a custom report to look into daily egress.

-   Example: Log Explorer -> Custom Reports -> Add/Remove charts -> Database API -> API Egress.

**What is contributing to Egress?**

While pointing out the exact cause for egress may not be straightforward, there are various steps you can take to determine the source of these issues:

-   Picking the "Top Paths" from the [log explorer](https://app.supabase.com/project/_/logs/explorer/templates) will help you identify heavily queried paths
-   By finding the most requested queries from Query performance report: [https://app.supabase.com/project/\_/reports/query-performance](https://app.supabase.com/project/_/reports/query-performance)
-   Supavisor Egress is independent of client. There is no direct relation between a single query and Supavisor egress, it is harder to debug and identify. But you can make use of frequent queries from the link in above step that also displays average number of rows which will help to identify queries with a large number of rows returned. While this does not display Supavisor queries specifically, it will give an overview of queries with lots of rows that can help.
-   For Storage Egress, all outgoing traffic for storage-related requests to download/view your Storage items are considered as Storage egress. We have a "Storage Egress Requests" template in logs explorer that you can use to get the number of requests for each Storage object
-   If you pull 1mb of data out of the database using the Supavisor connection in your edge function, but only sends 100kb back to the user, you will have the Egress from the Supavisor to your Edge function plus from the edge function to your user

**How can you decrease egress?**

-   Reduce the number of fields selected or entries when querying
-   Reduce the number of queries/calls by optimising client code or use caches to reduce the number of requests/queries being done: [https://github.com/psteinroe/supabase-cache-helpers/](https://github.com/psteinroe/supabase-cache-helpers/)
-   In case of update/insert queries, if you don’t need the entire row to be returned, configure your ORM/queries to not return the entire row
-   In case of running manual backups through Supavisor, remove unneeded tables and/or reduce the frequency
-   For Storage, if you start using the [Smart CDN](https://supabase.com/docs/guides/storage/cdn/smart-cdn) Storage Egress usage can be managed. You can also use the [Supabase Image Transformations](https://supabase.com/docs/guides/storage/image-transformations) to optimize the images and reduce the egress.

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Functions](https://supabase.com/docs/guides/troubleshooting?products=functions)[Storage](https://supabase.com/docs/guides/troubleshooting?products=storage)[Realtime](https://supabase.com/docs/guides/troubleshooting?products=realtime)[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Supavisor](https://supabase.com/docs/guides/troubleshooting?products=supavisor)

* * *

### Tags

[egress](https://supabase.com/docs/guides/troubleshooting?tags=egress)[bandwidth](https://supabase.com/docs/guides/troubleshooting?tags=bandwidth)

* * *

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