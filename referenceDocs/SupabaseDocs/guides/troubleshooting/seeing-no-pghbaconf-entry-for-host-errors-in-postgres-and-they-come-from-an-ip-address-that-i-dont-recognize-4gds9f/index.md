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

# Seeing "no pg\_hba.conf entry for host" errors in Postgres and they come from an IP address that I don't recognize

Last edited: 2/4/2025

* * *

"FATAL: no pg\_hba.conf entry for host" errors indicate that there was a failed authentication attempt to the database, so the connection couldn't be established.

The authentication failed because the user/password credentials were invalid: `(user "xxxx", database "yyyy")`. This could happen if you're trying to connect to the database using wrong or revoked credentials. These errors indicate a failed login attempt was made to your database, meaning the connection wasn't established.

It is common to see failed connection attempts that use default usernames (such as `user "pgbouncer"`, `database "postgres"`). Being on the public internet means some level of unauthorized access attempts are possible. These are very unsophisticated attempts that usually involve trying combinations like root, psql, test and Postgres usernames.

Supabase takes security seriously and works diligently to ensure the safety of your data.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[pg\_hba.conf](https://supabase.com/docs/guides/troubleshooting?tags=pg_hba.conf)[ip](https://supabase.com/docs/guides/troubleshooting?tags=ip)[authentication](https://supabase.com/docs/guides/troubleshooting?tags=authentication)

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