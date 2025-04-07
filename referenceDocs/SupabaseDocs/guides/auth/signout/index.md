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

3.  Flows (How-tos)

5.  [Signout](https://supabase.com/docs/guides/auth/signout)

# 

Signing out

## 

Signing out a user

* * *

Signing out a user works the same way no matter what method they used to sign in.

Call the sign out method from the client library. It removes the active session and clears Auth data from the storage medium.

JavaScriptDartSwiftKotlinPython

```
123async function signOut() {  const { error } = await supabase.auth.signOut()}
```

## Sign out and scopes[#](#sign-out-and-scopes)

Supabase Auth allows you to specify three different scopes for when a user invokes the [sign out API](https://supabase.com/docs/reference/javascript/auth-signout) in your application:

-   `global` (default) when all sessions active for the user are terminated.
-   `local` which only terminates the current session for the user but keep sessions on other devices or browsers active.
-   `others` to terminate all but the current session for the user.

You can invoke these by providing the `scope` option:

JavaScriptDartKotlin

```
12345// defaults to the global scopeawait supabase.auth.signOut()// sign out from the current session onlyawait supabase.auth.signOut({ scope: 'local' })
```

Upon sign out, all refresh tokens and potentially other database objects related to the affected sessions are destroyed and the client library removes the session stored in the local storage medium.

Access Tokens of revoked sessions remain valid until their expiry time, encoded in the `exp` claim. The user won't be immediately logged out and will only be logged out when the Access Token expires.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/signout.mdx)

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