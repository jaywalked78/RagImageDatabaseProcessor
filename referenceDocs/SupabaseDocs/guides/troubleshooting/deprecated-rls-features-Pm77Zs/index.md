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

# Deprecated RLS features

Last edited: 4/7/2025

* * *

## The `auth.role()` function is now deprecated[#](#the-authrole-function-is-now-deprecated)

The `auth.role()` function has been deprecated in favour of using the `TO` field, natively supported within Postgres:

```
12345678910111213-- DEPRECATEDcreate policy "Public profiles are viewable by everyone."on profiles for select using (  auth.role() = 'authenticated' or auth.role() = 'anon');-- RECOMMENDEDcreate policy "Public profiles are viewable by everyone."on profiles for selectto authenticated, anonusing (  true);
```

## The `auth.email()` function is now deprecated[#](#the-authemail-function-is-now-deprecated)

The `auth.email()` function has been deprecated in favour a more generic function to return the full JWT:

```
1234567891011- DEPRECATEDcreate policy "User can view their profile."on profiles for select using (  auth.email() = email);-- RECOMMENDEDcreate policy "User can view their profile."on profiles for select using (  (auth.jwt() ->> 'email') = email);
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[rls](https://supabase.com/docs/guides/troubleshooting?tags=rls)[deprecated](https://supabase.com/docs/guides/troubleshooting?tags=deprecated)[auth](https://supabase.com/docs/guides/troubleshooting?tags=auth)[policy](https://supabase.com/docs/guides/troubleshooting?tags=policy)

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