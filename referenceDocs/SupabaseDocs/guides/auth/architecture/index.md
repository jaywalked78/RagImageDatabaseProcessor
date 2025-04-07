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

3.  [Architecture](https://supabase.com/docs/guides/auth/architecture)

# 

Auth architecture

## 

The architecture behind Supabase Auth.

* * *

There are four major layers to Supabase Auth:

1.  [Client layer.](#client-layer) This can be one of the Supabase client SDKs, or manually made HTTP requests using the HTTP client of your choice.
2.  Kong API gateway. This is shared between all Supabase products.
3.  [Auth service](#auth-service) (formerly known as GoTrue).
4.  [Postgres database.](#postgres) This is shared between all Supabase products.

## Client layer[#](#client-layer)

The client layer runs in your app. This could be running in many places, including:

-   Your frontend browser code
-   Your backend server code
-   Your native application

The client layer provides the functions that you use to sign in and manage users. We recommend using the Supabase client SDKs, which handle:

-   Configuration and authentication of HTTP calls to the Supabase Auth backend
-   Persistence, refresh, and removal of Auth Tokens in your app's storage medium
-   Integration with other Supabase products

But at its core, this layer manages the making of HTTP calls, so you could write your own client layer if you wanted to.

See the Client SDKs for more information:

-   [JavaScript](https://supabase.com/docs/reference/javascript/introduction)
-   [Flutter](https://supabase.com/docs/reference/dart/introduction)
-   [Swift](https://supabase.com/docs/reference/swift/introduction)
-   [Python](https://supabase.com/docs/reference/python/introduction)
-   [C#](https://supabase.com/docs/reference/csharp/introduction)
-   [Kotlin](https://supabase.com/docs/reference/kotlin/introduction)

## Auth service[#](#auth-service)

The [Auth service](https://github.com/supabase/auth) is an Auth API server written and maintained by Supabase. It is a fork of the GoTrue project, originally created by Netlify.

When you deploy a new Supabase project, we deploy an instance of this server alongside your database, and inject your database with the required Auth schema.

The Auth service is responsible for:

-   Validating, issuing, and refreshing JWTs
-   Serving as the intermediary between your app and Auth information in the database
-   Communicating with external providers for Social Login and SSO

## Postgres[#](#postgres)

Supabase Auth uses the `auth` schema in your Postgres database to store user tables and other information. For security, this schema is not exposed on the auto-generated API.

You can connect Auth information to your own objects using [database triggers](https://supabase.com/docs/guides/database/postgres/triggers) and [foreign keys](https://www.postgresql.org/docs/current/tutorial-fk.html). Make sure that any views you create for Auth data are adequately protected by [enabling RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) or [revoking grants](https://www.postgresql.org/docs/current/sql-revoke.html).

Make sure any views you create for Auth data are protected.

Starting in Postgres version 15, views inherit the RLS policies of the underlying tables if created with `security_invoker`. Views in earlier versions, or those created without `security_invoker`, inherit the permissions of the owner, who can bypass RLS policies.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/architecture.mdx)

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