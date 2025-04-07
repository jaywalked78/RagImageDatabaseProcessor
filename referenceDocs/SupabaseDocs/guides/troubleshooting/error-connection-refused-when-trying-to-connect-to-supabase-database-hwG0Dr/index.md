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

# Error: "Connection refused" when trying to connect to Supabase database

Last edited: 1/18/2025

* * *

If you're not able to connect to the Supabase database and see the error `connect ECONNREFUSED 1.2.3.4:5432` or `psql: error: connection to server at "db.xxxxxxxxxxxxxxxxxxxx.supabase.co" (1.2.3.4), port 5432 failed: Connection refused Is the server running on that host and accepting TCP/IP connections?`, this could be because there are banned IPs on your project caused by Fail2ban as it kicks in when attempting 2 wrong passwords in a row.

These bans will clear after 30mins but you can unban the IPs using the Supabase CLI [https://supabase.com/docs/guides/cli](https://supabase.com/docs/guides/cli) following the commands below.

How to list the banned IPs:

```
1% supabase network-bans get --project-ref <project_reference_id> --experimental
```

How to unban the IPs:

```
1% supabase network-bans remove --db-unban-ip <ip_address> --project-ref <project_reference_id> --experimental
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Cli](https://supabase.com/docs/guides/troubleshooting?products=cli)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[connection](https://supabase.com/docs/guides/troubleshooting?tags=connection)[fail2ban](https://supabase.com/docs/guides/troubleshooting?tags=fail2ban)[econnrefused](https://supabase.com/docs/guides/troubleshooting?tags=econnrefused)

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