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

REST API

1.  [REST API](https://supabase.com/docs/guides/api)

3.  [Guides](https://supabase.com/docs/guides/api)

5.  [How API Keys work](https://supabase.com/docs/guides/api/api-keys)

# 

Understanding API Keys

* * *

Supabase provides two default keys when you create a project: an `anon` key, and a `service_role` key. You can find both keys in the [API Settings](https://supabase.com/dashboard/project/_/settings/api).

The data APIs are designed to work with Postgres Row Level Security (RLS). These keys both map to Postgres roles. You can find an `anon` user and a `service_role` user in the [Roles](http://supabase.com/dashboard/project/_/database/roles) section of the dashboard.

The keys are both long-lived JWTs. If you decode these keys, you will see that they contain the "role", an "issued date", and an "expiry date" ~10 years in the future.

```
12345{  "role": "anon",  "iat": 1625137684,  "exp": 1940713684}
```

## The `anon` key[#](#the-anon-key)

The `anon` key has very few privileges. You can use it in your [RLS policies](https://supabase.com/docs/guides/database/postgres/row-level-security) to allow unauthenticated access. For example, this policy will allow unauthenticated access to the `profiles` table:

```
123create policy "Allow public access" on profiles to anon forselect  using (true);
```

And similarly for disallowing access:

```
123create policy "Disallow public access" on profiles to anon forselect  using (false);
```

If you are using [Supabase Auth](https://supabase.com/docs/guides/auth/overview), then the `anon` role will automatically update to `authenticated` once a user is logged in:

```
123create policy "Allow access to authenticated users" on profiles to authenticated forselect  using (true);
```

## The `service_role` key[#](#the-servicerole-key)

The "service\_role" is a predefined Postgres role with elevated privileges, designed to perform various administrative and service-related tasks. It can bypass Row Level Security, so it should only be used on a private server.

Never expose the `service_role` key in a browser or anywhere where a user can see it.

A common use case for the `service_role` key is running data analytics jobs on the backend. To support joins on user id, it is often useful to grant the service role read access to `auth.users` table.

```
123grantselect  on table auth.users to service_role;
```

We have [partnered with GitHub](https://github.blog/changelog/2022-03-28-supabase-is-now-a-github-secret-scanning-partner/) to scan for Supabase `service_role` keys pushed to public repositories. If they detect any keys with service\_role privileges being pushed to GitHub, they will forward the API key to us, so that we can automatically revoke the detected secrets and notify you, protecting your data against malicious actors.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/api/api-keys.mdx)

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