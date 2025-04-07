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

# Database Error: remaining connection slots are reserved for non-replication superuser connections

Last edited: 1/18/2025

* * *

This error usually occurs when the database reaches the maximum number of connections allowed based on the compute add-on.

To overcome this, the connections need to be optimized as mentioned here: [https://supabase.com/docs/guides/platform/performance#optimizing-the-number-of-connections](https://supabase.com/docs/guides/platform/performance#optimizing-the-number-of-connections)

Additionally, you can try using the connection pool to help solve this issue: [https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)

If you're already using connection pooling and still hitting the maximum connections, then it is suggested to upgrade your compute add-on that allows more connections: [https://supabase.com/docs/guides/platform/compute-add-ons](https://supabase.com/docs/guides/platform/compute-add-ons)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[connections](https://supabase.com/docs/guides/troubleshooting?tags=connections)[connection slots](https://supabase.com/docs/guides/troubleshooting?tags=connection+slots)[reserved](https://supabase.com/docs/guides/troubleshooting?tags=reserved)[superuser](https://supabase.com/docs/guides/troubleshooting?tags=superuser)

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