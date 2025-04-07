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

# Database error saving new user

Last edited: 1/17/2025

* * *

You generally get this error when trying to invite a new user from the dashboard or when trying to insert a user into a table using the table editor in the Supabase dashboard.

This error is normally associated with a side effect of a database transaction.

**Common causes of this error:**

-   You have a trigger/trigger function setup on the `auth.users` table
-   You have added a constraint on the `auth.users` table which isn't being met
-   You are using Prisma and it has broken all the permissions on the `auth.users` table

**Debugging this error:**

-   You can use the [Auth logs explorer](https://app.supabase.com/project/_/logs/auth-logs) to find the issue with more information
-   You can use the [Postgres logs explorer](https://app.supabase.com/project/_/logs/postgres-logs)

[https://user-images.githubusercontent.com/79497/225517698-b6e3ccaf-cd70-4acd-8124-ffbcee310d63.mp4](https://user-images.githubusercontent.com/79497/225517698-b6e3ccaf-cd70-4acd-8124-ffbcee310d63.mp4)

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Studio](https://supabase.com/docs/guides/troubleshooting?products=studio)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[users](https://supabase.com/docs/guides/troubleshooting?tags=users)

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