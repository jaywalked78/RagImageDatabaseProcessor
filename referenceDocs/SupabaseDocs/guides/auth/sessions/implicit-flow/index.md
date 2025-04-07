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

3.  More

5.  [Sessions](https://supabase.com/docs/guides/auth/sessions)

7.  [Implicit flow](https://supabase.com/docs/guides/auth/sessions/implicit-flow)

# 

Implicit flow

## 

About authenticating with implicit flow.

* * *

The implicit flow is one of two ways that a user can authenticate and your app can receive the necessary access and refresh tokens.

The flow is an implementation detail handled for you by Supabase Auth, but understanding the difference between implicit and [PKCE flow](https://supabase.com/docs/guides/auth/sessions/pkce-flow) is important for understanding the difference between client-only and server-side auth.

## How it works[#](#how-it-works)

After a successful signin, the user is redirected to your app with a URL that looks like this:

```
1https://yourapp.com/...#access_token=<...>&refresh_token=<...>&...
```

The access and refresh tokens are contained in the URL fragment.

The client libraries:

-   Detect this type of URL
-   Extract the access token, refresh token, and some extra information
-   Persist this information to local storage for further use by the library and your app

## Limitations[#](#limitations)

The implicit flow only works on the client. Web browsers do not send the URL fragment to the server by design. This is a security feature:

-   You may be hosting your single-page app on a third-party server. The third-party service shouldn't get access to your user's credentials.
-   Even if the server is under your direct control, `GET` requests and their full URLs are often logged. This approach avoids leaking credentials in request or access logs.

If you wish to obtain the access token and refresh token on a server, use the [PKCE flow](https://supabase.com/docs/guides/auth/sessions/pkce-flow).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/sessions/implicit-flow.mdx)

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