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

# An "invalid response was received from the upstream server" error when querying auth

Last edited: 2/21/2025

* * *

If you are observing an "invalid response was received from the upstream server" error when making requests to Supabase Auth, it could mean that the respective service is down. One way to confirm this is to visit the [logs explorer](https://supabase.com/dashboard/project/_/logs/explorer) and look at the auth logs to see if there are any errors with the following lines:

-   `running db migrations: error executing migrations/20221208132122_backfill_email_last_sign_in_at.up.sql`

We're currently investigating an issue where the tables responsible for keeping track of migrations ran by Auth (`auth.schema_migrations`) are not being restored properly, which leads to the service(s) retrying those migrations. In such cases, migrations which are not idempotent will run into issues.

We've documented some of the migrations that run into this issue and their corresponding fix here:

### Auth: `operator does not exist: uuid = text`[#](#auth-operator-does-not-exist-uuid--text)

Temporary fix: Run `insert into auth.schema_migrations values ('20221208132122');` via the [SQL editor](https://supabase.com/dashboard/project/_/sql/new) to fix the issue.

If the migration error you're seeing looks different, reach out to [supabase.help](https://supabase.help/) for assistance.

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

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