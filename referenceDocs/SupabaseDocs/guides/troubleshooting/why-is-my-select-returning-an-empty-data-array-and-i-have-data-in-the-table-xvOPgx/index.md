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

# Why is my select returning an empty data array and I have data in the table?

Last edited: 2/21/2025

* * *

Usually this means you have RLS (row level security) enabled and no policy, or do not meet the policy. It can also mean you have a filter and have no rows matching that.

If you have RLS enabled you can test quickly by disable RLS on the table. If your query works then you have no policies or do not meet them.

If you have policies that depend on having a signed in user (TO set to `authenticated` or using `auth.uid()`) then you can check by setting TO as `anon` and setting your policy to just `TRUE`. If that works then you don't have a signed in user (with a JWT in the authorization header) when you make the call.

For more information on RLS see [https://supabase.com/docs/guides/auth/row-level-security](https://supabase.com/docs/guides/auth/row-level-security)

Adding: To test if you have a user session at time of your call you can add this function with the SQL editor and an RPC call in your code at same place as your current database call.

```
123456create function test_authorization_header() returns json    language SQL    as$$    select auth.jwt();$$;
```

```
12const { data: testData, error: testError } = await supabase.rpc('test_authorization_header')console.log(`The user role is ${testData.role} and the user UUID is ${testData.sub}. `, testError)
```

If you have anon or service\_role as the role then you do not have a user session at the time of your call.

To delete the test SQL function:

```
1drop function test_authorization_header;
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Tags

[rls](https://supabase.com/docs/guides/troubleshooting?tags=rls)[policy](https://supabase.com/docs/guides/troubleshooting?tags=policy)[filter](https://supabase.com/docs/guides/troubleshooting?tags=filter)[jwt](https://supabase.com/docs/guides/troubleshooting?tags=jwt)

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