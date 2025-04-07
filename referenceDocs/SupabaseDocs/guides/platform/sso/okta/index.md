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

3.  More

5.  [Single Sign-On](https://supabase.com/docs/guides/platform/sso)

7.  [SSO with Okta](https://supabase.com/docs/guides/platform/sso/okta)

# 

Set Up SSO with Okta

* * *

This feature is only available on the Team and Enterprise Plans. Contact [Sales](https://forms.supabase.com/enterprise) before doing these steps.

Looking for docs on how to add Single Sign-On support in your Supabase project? Head on over to [Single Sign-On with SAML 2.0 for Projects](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml).

Supabase supports single sign-on (SSO) using Okta.

## Step 1: Choose to create an app integration in the applications dashboard [#](#create-app-integration)

Navigate to the Applications dashboard of the Okta admin console. Click _Create App Integration_.

![Okta dashboard: Create App Integration button](https://supabase.com/docs/img/sso-okta-step-01.png)

## Step 2: Choose SAML 2.0 in the app integration dialog [#](#create-saml-app)

Supabase supports the SAML 2.0 SSO protocol. Choose it from the _Create a new app integration_ dialog.

![Okta dashboard: Create new app integration dialog](https://supabase.com/docs/img/sso-okta-step-02.png)

## Step 3: Fill out general settings [#](#add-general-settings)

The information you enter here is for visibility into your Okta applications menu. You can choose any values you like. `Supabase` as a name works well for most use cases.

![Okta dashboard: Create SAML Integration wizard](https://supabase.com/docs/img/sso-okta-step-03.png)

## Step 4: Fill out SAML settings [#](#add-saml-settings)

These settings let Supabase use SAML 2.0 properly with your Okta application. Make sure you enter this information exactly as shown on in this table and screenshot.

| Setting | Value |
| --- | --- |
| Single sign-on URL | `https://alt.supabase.io/auth/v1/sso/saml/acs` |
| Use this for Recipient URL and Destination URL | ✔️ |
| Audience URI (SP Entity ID) | `https://alt.supabase.io/auth/v1/sso/saml/metadata` |
| Default `RelayState` | `https://supabase.com/dashboard` |
| Name ID format | `EmailAddress` |
| Application username | Email |
| Update application username on | Create and update |

![Okta dashboard: Create SAML Integration wizard, Configure SAML step](https://supabase.com/docs/img/sso-okta-step-04.png)

## Step 5: Fill out attribute statements [#](#add-attribute-statements)

Attribute Statements allow Supabase to get information about your Okta users on each login.

**A `email` to `user.email` statement is required.** Other mappings shown below are optional and configurable depending on your Okta setup. If in doubt, replicate the same config as shown.

Share any changes, if any, from this screen with your Supabase support contact.

![Okta dashboard: Attribute Statements configuration screen](https://supabase.com/docs/img/sso-okta-step-05.png)

## Step 6: Obtain IdP metadata URL [#](#idp-metadata-url)

Supabase needs to finalize enabling single sign-on with your Okta application.

To do this scroll down to the _SAML Signing Certificates_ section on the _Sign On_ tab of the _Supabase_ application. Pick the the _SHA-2_ row with an _Active_ status. Click on the _Actions_ dropdown button and then on the _View IdP Metadata_.

This will open up the SAML 2.0 Metadata XML file in a new tab in your browser. Copy this URL and send it to your support contact and await further instructions. If you're not clear who to send this link to or need further assistance, contact [Supabase Support](https://supabase.help).

The link usually has this structure: `https://<okta-org>.okta.com/apps/<app-id>/sso/saml/metadata`

![Okta dashboard: SAML Signing Certificates, Actions button highlighted](https://supabase.com/docs/img/sso-okta-step-06.png)

## Step 7: Wait for confirmation [#](#confirmation)

Once you’ve configured the Okta app as shown above, make sure you send the [metadata URL](#idp-metadata-url) and information regarding the [attribute statements](#add-attribute-statements) (if any changes are applicable) to your support contact at Supabase.

Wait for confirmation that this information has successfully been added to Supabase. It usually takes us 1 business day to configure this information for you.

## Step 8: Test single sign-on [#](#testing)

Once you’ve received confirmation from your support contact at Supabase that SSO setup has been completed for your enterprise, you can ask some of your users to sign in via their Okta account.

You ask them to enter their email address on the [Sign in with SSO](https://supabase.com/dashboard/sign-in-sso) page.

If sign in is not working correctly, reach out to your support contact at Supabase for further guidance.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/sso/okta.mdx)

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