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

Auth

1.  Auth

3.  Third-party auth

5.  [Clerk](https://supabase.com/docs/guides/auth/third-party/clerk)

# 

Clerk

## 

Use Clerk with your Supabase project

* * *

Clerk can be used as a third-party authentication provider alongside Supabase Auth, or standalone, with your Supabase project.

## Getting started[#](#getting-started)

Getting started is incredibly easy. Start off by visiting [Clerk's Connect with Supabase page](https://dashboard.clerk.com/setup/supabase) to configure your Clerk instance for Supabase compatibility.

Finally add a [new Third-Party Auth integration with Clerk](https://supabase.com/dashboard/project/_/auth/third-party) in the Supabase dashboard.

### Configure for local development or self-hosting[#](#configure-for-local-development-or-self-hosting)

When developing locally or self-hosting with the Supabase CLI, add the following config to your `supabase/config.toml` file:

```
123[auth.third_party.clerk]enabled = truedomain = "example.clerk.accounts.dev"
```

You will still need to configure your Clerk instance for Supabase compatibility.

### Manually configuring your Clerk instance[#](#manually-configuring-your-clerk-instance)

If you are not able to use [Clerk's Connect with Supabase page](https://dashboard.clerk.com/setup/supabase) to configure your Clerk instance for working with Supabase, follow these steps.

1.  Add the `role` claim to [Clerk session tokens](https://clerk.com/docs/backend-requests/resources/session-tokens) by [customizing them](https://clerk.com/docs/backend-requests/custom-session-token). End-users who are authenticated should have the `authenticated` value for the claim. If you have an advanced Postgres setup where authenticated end-users use different Postgres roles to access the database, adjust the value to use the correct role name.
2.  Once all Clerk session tokens for your instance contain the `role` claim, add a [new Third-Party Auth integration with Clerk](https://supabase.com/dashboard/project/_/auth/third-party) in the Supabase dashboard or register it in the CLI as instructed above.

## Setup the Supabase client library[#](#setup-the-supabase-client-library)

TypeScriptFlutterSwift (iOS)

```
1234567import { createClient } from '@supabase/supabase-js'const supabase = createClient('https://<supabase-project>.supabase.co', 'SUPABASE_ANON_KEY', {  accessToken: () => {    return Clerk.session?.getToken()  },})
```

## Using RLS policies[#](#using-rls-policies)

Once you've configured the Supabase client library to use Clerk session tokens, you can use RLS policies to secure access to your project's database, Storage objects and Realtime channels.

The recommended way to design RLS policies with Clerk is to use claims present in your Clerk session token to allow or reject access to your project's data. Check [Clerk's docs](https://clerk.com/docs/backend-requests/resources/session-tokens) on the available JWT claims and their values.

### Example: Check user organization role[#](#example-check-user-organization-role)

```
123456789create policy "Only organization admins can insert in table"  on table_name  for insert  to authenticated  with check (    ((select auth.jwt()->>'org_role') = 'org:admin')      and    (organization_id = (select auth.jwt()->>'org_id'))  );
```

This RLS policy checks that the newly inserted row in the table has the user's declared organization ID (from the `org_id` session token claim) in the `organization_id` column. Additionally it ensures that they're an `org:admin`.

This way only organization admins can add rows to the table, for organizations they're a member of.

### Example: Check user has passed second factor verification[#](#example-check-user-has-passed-second-factor-verification)

```
12345678create policy "Only users that have passed second factor verification can read from table"  on table_name  for select  as restrictive  to authenticated  using (    ((select auth.jwt()->'fva'->>1) != '-1')  );
```

This example uses a restrictive RLS policy checks that the [second factor verification](https://clerk.com/docs/guides/reverification) age element in the `fva` claim is not `'-1'` indicating the user has passed through second factor verification.

## Deprecated integration with JWT templates[#](#deprecated-integration-with-jwt-templates)

As of 1st April 2025 the previously available [Clerk Integration with Supabase](https://supabase.com/partners/integrations/clerk) is considered deprecated and is no longer recommended for use. All projects using the deprecated integration will be excluded from Third-Party Monthly Active User (TP-MAU) charges until at least 1st January 2026.

This integration used low-level primitives that are still available in Supabase and Clerk, such as a [configurable JWT secret](https://supabase.com/dashboard/project/_/settings/api) and [JWT templates from Clerk](https://clerk.com/docs/backend-requests/jwt-templates). This enables you to keep using it in an unofficial manner, though only limited support will be provided from Supabase.

Deprecation is done for the following reasons:

-   Sharing your project's JWT secret with a third-party is a problematic security practice
-   Rotating the project's JWT secret in this case almost always results in significant downtime for your application
-   Additional latency to [generate a new JWT](https://clerk.com/docs/backend-requests/jwt-templates#generate-a-jwt) for use with Supabase, instead of using the Clerk [session tokens](https://clerk.com/docs/backend-requests/resources/session-tokens)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/third-party/clerk.mdx)

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