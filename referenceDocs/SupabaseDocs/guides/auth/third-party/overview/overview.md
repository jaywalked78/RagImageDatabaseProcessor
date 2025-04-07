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

5.  [Overview](https://supabase.com/docs/guides/auth/third-party/overview)

# 

Third-party auth

## 

First-class support for authentication providers

* * *

Supabase has first-class support for these third-party authentication providers:

-   [Clerk](https://supabase.com/docs/guides/auth/third-party/clerk)
-   [Firebase Auth](https://supabase.com/docs/guides/auth/third-party/firebase-auth)
-   [Auth0](https://supabase.com/docs/guides/auth/third-party/auth0)
-   [AWS Cognito (with or without AWS Amplify)](https://supabase.com/docs/guides/auth/third-party/aws-cognito)

You can use these providers alongside Supabase Auth, or on their own, to access the [Data API (REST and GraphQL)](https://supabase.com/docs/guides/database), [Storage](https://supabase.com/docs/guides/storage), [Realtime](https://supabase.com/docs/guides/storage) and [Functions](https://supabase.com/docs/guides/functions) from your existing apps.

If you already have production apps using one of these authentication providers, and would like to use a Supabase feature, you no longer need to migrate your users to Supabase Auth or use workarounds like translating JWTs into the Supabase Auth format and using your project's signing secret.

## How does it work?[#](#how-does-it-work)

To use Supabase products like Data APIs for your Postgres database, Storage or Realtime, you often need to send access tokens or JWTs via the Supabase client libraries or via the REST API. Third-party auth support means that when you add a new integration with one of these providers, the API will trust JWTs issued by the provider similar to how it trusts JWTs issued by Supabase Auth.

This is made possible if the providers are using JWTs signed with asymmetric keys, which means that the Supabase APIs will be able to only verify but not create JWTs.

## Limitations[#](#limitations)

There are some limitations you should be aware of when using third-party authentication providers with Supabase.

1.  The third-party provider must use asymmetrically signed JWTs (exposed as an OIDC Issuer Discovery URL by the third-party authentication provider). Using symmetrically signed JWTs is not possible at this time.
2.  The JWT signing keys from the third-party provider are stored in the configuration of your project, and are checked for changes periodically. If you are rotating your keys (when supported) allow up to 30 minutes for the change to be picked up.
3.  It is not possible to disable Supabase Auth at this time.

## Pricing[#](#pricing)

$0.00325 per Third-Party MAU. You are only charged for usage exceeding your subscription plan's quota.

For a detailed breakdown of how charges are calculated, refer to [Manage Monthly Active Third-Party Users usage](https://supabase.com/docs/guides/platform/manage-your-usage/monthly-active-users-third-party).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/third-party/overview.mdx)

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