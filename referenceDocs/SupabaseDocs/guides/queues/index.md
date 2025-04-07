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

Queues

1.  [Queues](https://supabase.com/docs/guides/queues)

3.  [Overview](https://supabase.com/docs/guides/queues)

# 

Supabase Queues

## 

Durable Message Queues with Guaranteed Delivery in Postgres

* * *

Supabase Queues is a Postgres-native durable Message Queue system with guaranteed delivery built on the [pgmq database extension](https://github.com/tembo-io/pgmq). It offers developers a seamless way to persist and process Messages in the background while improving the resiliency and scalability of their applications and services.

Queues couples the reliability of Postgres with the simplicity Supabase's platform and developer experience, enabling developers to manage Background Tasks with zero configuration.

## Features[#](#features)

-   **Postgres Native**  
    Built on top of the `pgmq` database extension, create and manage Queues with any Postgres tooling.
-   **Guaranteed Message Delivery**  
    Messages added to Queues are guaranteed to be delivered to your consumers.
-   **Exactly Once Message Delivery**  
    A Message is delivered exactly once to a consumer within a customizable visibility window.
-   **Message Durability and Archival**  
    Messages are stored in Postgres and you can choose to archive them for analytical or auditing purposes.
-   **Granular Authorization**  
    Control client-side consumer access to Queues with API permissions and Row Level Security (RLS) policies.
-   **Queue Management and Monitoring**  
    Create, manage, and monitor Queues and Messages in the Supabase Dashboard.

## Resources[#](#resources)

-   [Quickstart](https://supabase.com/docs/guides/queues/quickstart)
-   [API Reference](https://supabase.com/docs/guides/queues/api)
-   [`pgmq` GitHub Repository](https://github.com/tembo-io/pgmq)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/queues.mdx)

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