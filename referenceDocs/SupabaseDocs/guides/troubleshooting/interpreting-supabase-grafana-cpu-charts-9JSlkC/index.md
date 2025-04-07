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

# Interpreting Supabase Grafana CPU charts

Last edited: 1/17/2025

* * *

> [Guide](https://supabase.com/docs/guides/monitoring-troubleshooting/metrics#deploying-supabase-grafana) for setting up Supabase Grafana

# CPU

Here are examples of unhealthy CPU utilization:

![image](https://supabase.com/docs/img/troubleshooting/e7d78109-b09d-48ca-8cc6-e4913693e163.png) ![image](https://supabase.com/docs/img/troubleshooting/49e175d9-6338-4b17-97be-4bf7853e319f.png)

The CPU chart shows 4 distinct metrics of interest:

-   **Yellow**: It represents CPU utilized in [kernel space](https://en.wikipedia.org/wiki/User_space_and_kernel_space) (privileged OS operations). If this is high, it may be a sign that your app is connecting/disconnecting too aggressively. It could also be symptomatic of extension-related errors.
-   **Blue**: It represents requests in user space and mainly reflects the CPU usage from regular queries. For optimization tips, check out the links at the end of the page.
-   **Red**: It represents cycles the CPU spent idle because it was waiting on IO tasks. Any amount of red often implies [disk](https://github.com/orgs/supabase/discussions/27003) or, indirectly, [memory](https://github.com/orgs/supabase/discussions/27021) problems. The links outline how to address this type of issue.
-   **Green**: These are CPU cycles spent idle.

As the CPU peaks towards 100%, queries and database tasks will begin to throttle, as they won't have enough time or access to the CPU.

### Other useful Supabase Grafana guides:[#](#other-useful-supabase-grafana-guides)

-   [Connections](https://github.com/orgs/supabase/discussions/27141)
-   [Disk](https://github.com/orgs/supabase/discussions/27003)
-   [Memory](https://github.com/orgs/supabase/discussions/27021)

### Optimizing:[#](#optimizing)

1.  [Optimize your queries](https://supabase.com/docs/guides/database/query-optimization).
2.  [Add indexes](https://github.com/orgs/supabase/discussions/22449) if possible.
3.  [Increasing the compute size](https://supabase.com/docs/guides/platform/compute-add-ons)
4.  [Distribute load by using read-replicas](https://supabase.com/dashboard/project/_/settings/infrastructure)

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[cpu](https://supabase.com/docs/guides/troubleshooting?tags=cpu)[grafana](https://supabase.com/docs/guides/troubleshooting?tags=grafana)[metrics](https://supabase.com/docs/guides/troubleshooting?tags=metrics)

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