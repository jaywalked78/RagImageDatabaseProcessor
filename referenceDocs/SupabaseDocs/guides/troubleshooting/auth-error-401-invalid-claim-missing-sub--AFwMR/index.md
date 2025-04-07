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

# Auth error: {401: invalid claim: missing sub}

Last edited: 2/4/2025

* * *

The missing sub claim error is returned when `supabase.auth.getUser()` is called with an invalid JWT in the session or when the user attempts to register/sign in but hasn't completed the sign in when the `getUser` call is made.

A common pitfall, is inadvertently using a Supabase API key (such as the anon or service\_role keys) instead of the Supabase Auth access token.

**Why Does This Happen?**

-   The Supabase API keys are designed for different purposes and, while they are recognized by the Supabase Auth system, they do not carry the sub claim. The sub claim is essential as it encodes the user ID, which is a mandatory field for authentication processes. This mistake leads to the "missing sub claim" error because the system expects a token that contains user identification information.

**How to Avoid This Issue:**

-   Ensure that the token being passed to `supabase.auth.getUser()` is, indeed, an Auth access token and not one of the API keys.
    
-   Are you creating the client on a per-request basis or are you creating a global client to be shared? If you're creating the client on a per-request basis, then you need to pass the session with the user's JWT from the client to the server somehow. This can be done by sending the user's JWT in a header like an `Authorization: Bearer <user_jwt>` . You can then get this header and call `supabase.auth.getUser(user_jwt)` with the user's JWT.
    
-   Examine how the Supabase client is being initialized, especially in server-side scenarios.
    

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Related error codes

[401](https://supabase.com/docs/guides/troubleshooting?errorCodes=401)[403](https://supabase.com/docs/guides/troubleshooting?errorCodes=403)

* * *

### Tags

[JWT](https://supabase.com/docs/guides/troubleshooting?tags=JWT)[Server-Side Rendering](https://supabase.com/docs/guides/troubleshooting?tags=Server-Side+Rendering)

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