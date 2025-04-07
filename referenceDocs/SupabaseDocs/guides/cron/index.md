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

Cron

1.  [Cron](https://supabase.com/docs/guides/cron)

3.  [Overview](https://supabase.com/docs/guides/cron)

# 

Cron

## 

Schedule Recurring Jobs with Cron Syntax in Postgres

* * *

Supabase Cron is a Postgres Module that simplifies scheduling recurring Jobs with cron syntax and monitoring Job runs inside Postgres.

Cron Jobs can be created via SQL or the Cron interface inside of Supabase Dashboard and can run anywhere from every second to once a year depending on your use case.

Every Job can run SQL snippets or database functions with zero network latency or make an HTTP request, such as invoking a Supabase Edge Function, with ease.

For best performance, we recommend no more than 8 Jobs run concurrently. Each Job should run no more than 10 minutes.

## How does Cron work?[#](#how-does-cron-work)

Under the hood, Supabase Cron uses the [`pg_cron`](https://github.com/citusdata/pg_cron) Postgres database extension which is the scheduling and execution engine for your Jobs.

`pg_cron` is not fully supported on Fly Postgres. Learn more about [Fly Postgres limitations](https://supabase.com/docs/guides/platform/fly-postgres#limitations).

The extension creates a `cron` schema in your database and all Jobs are stored on the `cron.job` table. Every Job's run and its status is recorded on the `cron.job_run_details` table.

The Supabase Dashboard provides and interface for you to schedule Jobs and monitor Job runs. You can also do the same with SQL.

## Resources[#](#resources)

-   [`pg_cron` GitHub Repository](https://github.com/citusdata/pg_cron)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/cron.mdx)

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