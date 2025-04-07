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

# How to delete a role in Postgres

Last edited: 2/21/2025

* * *

[Quote from Postgres docs:](https://www.postgresql.org/docs/current/sql-droprole.html#:~:text=A%20role%20cannot%20be%20removed,been%20granted%20on%20other%20objects.)

> A role cannot be removed if it is still referenced in any database of the cluster; an error will be raised if so. Before dropping the role, you must drop all the objects it owns (or reassign their ownership) and revoke any privileges the role has been granted on other objects.

First make sure that Postgres has ownership over the role:

```
1GRANT <role> TO "postgres";
```

Then you must reassign any objects owned by role:

```
1REASSIGN OWNED BY <role> TO postgres;
```

Once ownership is transferred, you can run the following query:

```
1DROP OWNED BY <role>;
```

[DROP OWNED BY](https://www.postgresql.org/docs/current/sql-drop-owned.html) does delete all objects owned by the role, which should be none. However, it also revokes the role's privileges. Once this is done, you should be able to run:

```
1DROP role <role>;
```

If you encounter any issues, create a [support ticket](https://supabase.com/dashboard/support/new)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[role](https://supabase.com/docs/guides/troubleshooting?tags=role)[delete](https://supabase.com/docs/guides/troubleshooting?tags=delete)[postgres](https://supabase.com/docs/guides/troubleshooting?tags=postgres)

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