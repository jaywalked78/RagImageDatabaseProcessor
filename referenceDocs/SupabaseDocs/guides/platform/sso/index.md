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

5.  [Single Sign-On](https://supabase.com/docs/guides/platform/sso)

# 

Enable SSO for Your Organization

* * *

Looking for docs on how to add Single Sign-On support in your Supabase project? Head on over to [Single Sign-On with SAML 2.0 for Projects](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml).

Supabase offers single sign-on (SSO) as a login option to provide additional account security for your team. This allows company administrators to enforce the use of an identity provider when logging into Supabase. SSO improves the onboarding and offboarding experience of the company as the employee only needs a single set of credentials to access third-party applications or tools which can also be revoked by an administrator.

Supabase currently provides SAML SSO for [Team and Enterprise plan customers](https://supabase.com/pricing). Contact [Sales](https://forms.supabase.com/team) to have this enabled for your organization.

## Setup and limitations[#](#setup-and-limitations)

Supabase supports practically all identity providers that support the SAML 2.0 SSO protocol. We've prepared these guides for commonly used identity providers to help you get started. If you use a different provider, our support stands ready to support you.

-   [Google Workspaces (formerly G Suite)](https://supabase.com/docs/guides/platform/sso/gsuite)
-   [Azure Active Directory](https://supabase.com/docs/guides/platform/sso/azure)
-   [Okta](https://supabase.com/docs/guides/platform/sso/okta)

Accounts signing in with SSO have certain limitations. The following sections outline the limitations when SSO is enabled or disabled for your team.

### Enable SSO for your team [#](#enable-sso)

-   Organization invites are restricted to company members belonging to the same identity provider.
-   Every user has an organization created by default. They can create as many projects as they want.
-   An SSO user will not be able to update or reset their password since the company administrator manages their access via the identity provider.
-   If an SSO user with the following email of `alice@foocorp.com` attempts to sign in with a GitHub account that uses the same email, a separate Supabase account is created and will not be linked to the SSO user's account.
-   An SSO user will not be able to see all organizations/projects created under the same identity provider. They will need to be invited to the Supabase organization first. Refer to [access control](https://supabase.com/docs/guides/platform/access-control) for more information.

### Disable SSO for your team [#](#disable-sso)

-   You can prevent a user's account from further access to Supabase by removing or disabling their account in your identity provider.
-   You should also remove or downgrade their permissions from any organizations inside Supabase.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/sso.mdx)

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