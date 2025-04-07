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

# NEW variable is null in a trigger function.

Last edited: 1/16/2025

* * *

When you create a function and call it from a trigger the NEW variable is only passed in if the trigger is on ROW operations

The UI currently defaults to STATEMENT which will not provide NEW or OLD variables to the function.

![image](https://supabase.com/docs/img/troubleshooting/49e11154-296b-42b9-8036-8a7288e49b8a.png)

Also in SQL (reference: [https://www.postgresql.org/docs/current/sql-createtrigger.html](https://www.postgresql.org/docs/current/sql-createtrigger.html))

![image](https://supabase.com/docs/img/troubleshooting/c7ac0f69-6fb9-4ff2-8aab-5cda6bada3f6.png)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Functions](https://supabase.com/docs/guides/troubleshooting?products=functions)

* * *

### Tags

[trigger](https://supabase.com/docs/guides/troubleshooting?tags=trigger)[function](https://supabase.com/docs/guides/troubleshooting?tags=function)[statement](https://supabase.com/docs/guides/troubleshooting?tags=statement)[row](https://supabase.com/docs/guides/troubleshooting?tags=row)[NEW](https://supabase.com/docs/guides/troubleshooting?tags=NEW)[OLD](https://supabase.com/docs/guides/troubleshooting?tags=OLD)[SQL](https://supabase.com/docs/guides/troubleshooting?tags=SQL)

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