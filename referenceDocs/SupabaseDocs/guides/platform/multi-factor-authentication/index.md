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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  Project & Account Management

5.  [Multi-factor Authentication](https://supabase.com/docs/guides/platform/multi-factor-authentication)

# 

Multi-factor Authentication

## 

Enable multi-factor authentication (MFA) to keep your account secure.

* * *

This guide is for adding MFA to your Supabase user account. If you want to enable MFA for users in your Supabase project, refer to [**this guide**](https://supabase.com/docs/guides/auth/auth-mfa) instead.

Multi-factor authentication (MFA) adds an additional layer of security to your user account, by requiring a second factor to verify your user identity. Supabase allows users to enable MFA on their account and set it as a requirement for subsequent logins.

## Supported authentication factors[#](#supported-authentication-factors)

Currently, Supabase supports adding a unique time-based one-time password (TOTP) to your user account as an additional security factor. You can manage your TOTP factor using apps such as 1Password, Authy, Google Authenticator or Apple's Keychain.

## Enable MFA[#](#enable-mfa)

You can enable MFA for your user account under your [Supabase account settings](https://supabase.com/dashboard/account/security). Enabling MFA will result in all other user sessions to be automatically logged out and forced to sign-in again with MFA.

Supabase does not return recovery codes. Instead, we recommend that you register a backup TOTP factor to use in an event that you lose access to your primary TOTP factor. Make sure you use a different device and app, or store the secret in a secure location different than your primary one.

For security reasons, we will not be able to restore access to your account if you lose all your two-factor authentication credentials. Do register a backup factor if necessary.

## Login with MFA[#](#login-with-mfa)

Once you've enabled MFA for your Supabase user account, you will be prompted to enter your second factor challenge code as seen in your preferred TOTP app.

## Disable MFA[#](#disable-mfa)

You can disable MFA for your user account under your [Supabase account settings](https://supabase.com/dashboard/account/security). On subsequent login attempts, you will not be prompted to enter a MFA code.

We strongly recommend that you do not disable MFA to avoid unauthorized access to your user account.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/multi-factor-authentication.mdx)

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