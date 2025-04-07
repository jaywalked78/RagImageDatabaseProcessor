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

5.  [Identity Linking](https://supabase.com/docs/guides/auth/auth-identity-linking)

# 

Identity Linking

## 

Manage the identities associated with your user

* * *

## Identity linking strategies[#](#identity-linking-strategies)

Currently, Supabase Auth supports 2 strategies to link an identity to a user:

1.  [Automatic Linking](#automatic-linking)
2.  [Manual Linking](#manual-linking-beta)

### Automatic linking[#](#automatic-linking)

Supabase Auth automatically links identities with the same email address to a single user. This helps to improve the user experience when multiple OAuth login options are presented since the user does not need to remember which OAuth account they used to sign up with. When a new user signs in with OAuth, Supabase Auth will attempt to look for an existing user that uses the same email address. If a match is found, the new identity is linked to the user.

In order for automatic linking to correctly identify the user for linking, Supabase Auth needs to ensure that all user emails are unique. It would also be an insecure practice to automatically link an identity to a user with an unverified email address since that could lead to pre-account takeover attacks. To prevent this from happening, when a new identity can be linked to an existing user, Supabase Auth will remove any other unconfirmed identities linked to an existing user.

Users that signed up with [SAML SSO](https://supabase.com/docs/guides/auth/sso/auth-sso-saml) will not be considered as targets for automatic linking.

### Manual linking (beta)[#](#manual-linking-beta)

JavaScriptDartSwiftKotlinPython

Supabase Auth allows a user to initiate identity linking with a different email address when they are logged in. To link an OAuth identity to the user, call [`linkIdentity()`](https://supabase.com/docs/reference/javascript/auth-linkidentity):

```
1const { data, error } = await supabase.auth.linkIdentity({ provider: 'google' })
```

In the example above, the user will be redirected to Google to complete the OAuth2.0 flow. Once the OAuth2.0 flow has completed successfully, the user will be redirected back to the application and the Google identity will be linked to the user. You can enable manual linking from your project's authentication [configuration options](https://supabase.com/dashboard/project/_/settings/auth) or by setting the environment variable `GOTRUE_SECURITY_MANUAL_LINKING_ENABLED: true` when self-hosting.

## Unlink an identity[#](#unlink-an-identity)

JavaScriptDartSwiftKotlinPython

You can use [`getUserIdentities()`](https://supabase.com/docs/reference/javascript/auth-getuseridentities) to fetch all the identities linked to a user. Then, call [`unlinkIdentity()`](https://supabase.com/docs/reference/javascript/auth-unlinkidentity) to unlink the identity. The user needs to be logged in and have at least 2 linked identities in order to unlink an existing identity.

```
12345678910// retrieve all identities linked to a userconst {  data: { identities },} = await supabase.auth.getUserIdentities()// find the google identity linked to the userconst googleIdentity = identities.find((identity) => identity.provider === 'google')// unlink the google identity from the userconst { data, error } = await supabase.auth.unlinkIdentity(googleIdentity)
```

## Frequently asked questions[#](#frequently-asked-questions)

### How to add email/password login to an OAuth account?[#](#how-to-add-emailpassword-login-to-an-oauth-account)

Call the `updateUser({ password: 'validpassword'})` to add email with password authentication to an account created with an OAuth provider (Google, GitHub, etc.).

### Can you sign up with email if already using OAuth?[#](#can-you-sign-up-with-email-if-already-using-oauth)

If you try to create an email account after previously signing up with OAuth using the same email, you'll receive an obfuscated user response with no verification email sent. This prevents user enumeration attacks.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/auth-identity-linking.mdx)

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