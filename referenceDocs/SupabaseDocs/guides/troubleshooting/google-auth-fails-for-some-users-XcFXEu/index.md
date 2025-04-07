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

# Google Auth fails for some users

Last edited: 1/17/2025

* * *

## Google Auth fails for some users[#](#google-auth-fails-for-some-users)

If you start facing either of these errors:

```
12345678910error=server_error&error_description=Error+getting+user+email+from+external+providerMissing required authentication credential.Expected OAuth 2 access token, login cookie or other valid authentication credential.See https://developers.google.com/identity/sign-in/web/devconsole-project.\",\n \"status\": \"UNAUTHENTICATED\" } "level":"error","method":"GET","msg":"500: Error getting user email from external provider","path":"/callback","referer":"https://accounts.google.com/","remote_addr":"x.x.X.x","time":"2023-06-06T21:46:11Z","timestamp":"2023-06-06T21:46:11Z"}
```

It is happening because some Google Suite requires the explicit request of email Auth Scopes: `https://www.googleapis.com/auth/userinfo.email`

```
123456const { data, error } = await supabase.auth.signInWithOAuth({  provider: 'google'  options: {    scopes: 'https://www.googleapis.com/auth/userinfo.email'  }})
```

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Related error codes

[500 server\_error](https://supabase.com/docs/guides/troubleshooting?errorCodes=500+server_error)[401 UNAUTHENTICATED](https://supabase.com/docs/guides/troubleshooting?errorCodes=401+UNAUTHENTICATED)

* * *

### Tags

[OAuth](https://supabase.com/docs/guides/troubleshooting?tags=OAuth)[Google](https://supabase.com/docs/guides/troubleshooting?tags=Google)[credential](https://supabase.com/docs/guides/troubleshooting?tags=credential)[email](https://supabase.com/docs/guides/troubleshooting?tags=email)

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