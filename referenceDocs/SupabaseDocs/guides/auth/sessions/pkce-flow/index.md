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

7.  [PKCE flow](https://supabase.com/docs/guides/auth/sessions/pkce-flow)

# 

PKCE flow

## 

About authenticating with PKCE flow.

* * *

The Proof Key for Code Exchange (PKCE) flow is one of two ways that a user can authenticate and your app can receive the necessary access and refresh tokens.

The flow is an implementation detail handled for you by Supabase Auth, but understanding the difference between PKCE and [implicit flow](https://supabase.com/docs/guides/auth/sessions/implicit-flow) is important for understanding the difference between client-only and server-side auth.

## How it works[#](#how-it-works)

After a successful verification, the user is redirected to your app with a URL that looks like this:

```
1https://yourapp.com/...?code=<...>
```

The `code` parameter is commonly known as the Auth Code and can be exchanged for an access token by calling `exchangeCodeForSession(code)`.

For security purposes, the code has a validity of 5 minutes and can only be exchanged for an access token once. You will need to restart the authentication flow from scratch if you wish to obtain a new access token.

As the flow is run server side, `localStorage` may not be available. You may configure the client library to use a custom storage adapter and an alternate backing storage such as cookies by setting the `storage` option to an object with the following methods:

```
1234567891011121314151617181920212223const customStorageAdapter: SupportedStorage = {    getItem: (key) => {    if (!supportsLocalStorage()) {        // Configure alternate storage        return null    }    return globalThis.localStorage.getItem(key)    },    setItem: (key, value) => {    if (!supportsLocalStorage()) {        // Configure alternate storage here        return    }    globalThis.localStorage.setItem(key, value)    },    removeItem: (key) => {    if (!supportsLocalStorage()) {        // Configure alternate storage here        return    }    globalThis.localStorage.removeItem(key)    },}
```

You may also configure the client library to automatically exchange it for a session after a successful redirect. This can be done by setting the `detectSessionInUrl` option to `true`.

Putting it all together, your client library initialization may look like this:

```
1234567891011121314const supabase = createClient(        'https://xyzcompany.supabase.co',        'public-anon-key',        {        ...        auth: {            ...            detectSessionInUrl: true,            flowType: 'pkce',            storage: customStorageAdapter,        }        ...        })
```

## Limitations[#](#limitations)

Behind the scenes, the code exchange requires a code verifier. Both the code in the URL and the code verifier are sent back to the Auth server for a successful exchange.

The code verifier is created and stored locally when the Auth flow is first initiated. That means the code exchange must be initiated on the same browser and device where the flow was started.

## Resources[#](#resources)

-   [OAuth 2.0 guide](https://oauth.net/2/pkce/) to PKCE flow

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/sessions/pkce-flow.mdx)

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