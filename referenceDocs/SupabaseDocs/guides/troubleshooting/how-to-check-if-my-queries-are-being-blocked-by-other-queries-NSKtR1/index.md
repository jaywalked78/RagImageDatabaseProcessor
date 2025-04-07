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

# How to check if my queries are being blocked by other queries?

Last edited: 1/17/2025

* * *

## You can set a lock monitor view to help investigate these.[#](#you-can-set-a-lock-monitor-view-to-help-investigate-these)

Once you run the query that takes a long time to complete, you can go in the dashboard (or select from this view below) to check what are the blocks.

```
12345678910111213141516171819202122232425262728create view  public.lock_monitor asselect  coalesce(    blockingl.relation::regclass::text,    blockingl.locktype  ) as locked_item,  now() - blockeda.query_start as waiting_duration,  blockeda.pid as blocked_pid,  blockeda.query as blocked_query,  blockedl.mode as blocked_mode,  blockinga.pid as blocking_pid,  blockinga.query as blocking_query,  blockingl.mode as blocking_modefrom  pg_locks blockedl  join pg_stat_activity blockeda on blockedl.pid = blockeda.pid  join pg_locks blockingl on (    blockingl.transactionid = blockedl.transactionid    or blockingl.relation = blockedl.relation    and blockingl.locktype = blockedl.locktype  )  and blockedl.pid <> blockingl.pid  join pg_stat_activity blockinga on blockingl.pid = blockinga.pid  and blockinga.datid = blockeda.datidwhere  not blockedl.granted  and blockinga.datname = current_database();
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

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