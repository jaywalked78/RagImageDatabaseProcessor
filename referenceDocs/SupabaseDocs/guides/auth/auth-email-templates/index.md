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

3.  Configuration

5.  [Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)

# 

Email Templates

## 

Learn how to manage the email templates in Supabase.

* * *

You can customize the email messages used for the authentication flows. You can edit the following email templates:

-   Confirm signup
-   Invite user
-   Magic Link
-   Change Email Address
-   Reset Password

## Terminology[#](#terminology)

The templating system provides the following variables for use:

| Name | Description |
| --- | --- |
| `{{ .ConfirmationURL }}` | Contains the confirmation URL. For example, a signup confirmation URL would look like: `https://project-ref.supabase.co/auth/v1/verify?token={{ .TokenHash }}&type=email&redirect_to=https://example.com/path` . |
| `{{ .Token }}` | Contains a 6-digit One-Time-Password (OTP) that can be used instead of the `{{. ConfirmationURL }}` . |
| `{{ .TokenHash }}` | Contains a hashed version of the `{{ .Token }}`. This is useful for constructing your own email link in the email template. |
| `{{ .SiteURL }}` | Contains your application's Site URL. This can be configured in your project's [authentication settings](https://supabase.com/dashboard/project/_/auth/url-configuration). |
| `{{ .RedirectTo }}` | Contains the redirect URL passed when `signUp`, `signInWithOtp`, `signInWithOAuth`, `resetPasswordForEmail` or `inviteUserByEmail` is called. The redirect URL allow list can be configured in your project's [authentication settings](https://supabase.com/dashboard/project/_/auth/url-configuration). |
| `{{ .Data }}` | Contains metadata from `auth.users.user_metadata`. Use this to personalize the email message. |

## Editing email templates[#](#editing-email-templates)

On hosted Supabase projects, edit your email templates on the [Email Templates](https://supabase.com/dashboard/project/_/auth/templates) page. On self-hosted projects or in local development, edit your [configuration files](https://supabase.com/docs/guides/local-development/customizing-email-templates).

## Mobile deep linking[#](#mobile-deep-linking)

For mobile applications, you might need to link or redirect to a specific page within your app. See the [Mobile Deep Linking guide](https://supabase.com/docs/guides/auth/native-mobile-deep-linking) to set this up.

## Limitations[#](#limitations)

### Email prefetching[#](#email-prefetching)

Certain email providers may have spam detection or other security features that prefetch URL links from incoming emails (e.g. [Safe Links in Microsoft Defender for Office 365](https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/safe-links-about?view=o365-worldwide)). In this scenario, the `{{ .ConfirmationURL }}` sent will be consumed instantly which leads to a "Token has expired or is invalid" error. To guard against this:

-   Use an email OTP instead by including `{{ .Token }}` in the email template.
    
-   Create your own custom email link to redirect the user to a page where they can click on a button to confirm the action. For example, you can include the following in your email template:
    
    ```
    123<a href="{{ .SiteURL }}/confirm-signup?confirmation_url={{ .ConfirmationURL }}"  >Confirm your signup</a>
    ```
    
    The user should be brought to a page on your site where they can confirm the action by clicking a button. The button should contain the actual confirmation link which can be obtained from parsing the `confirmation_url={{ .ConfirmationURL }}` query parameter in the URL.
    

### Email tracking[#](#email-tracking)

If you are using an external email provider that enables "email tracking", the links inside the Supabase email templates will be overwritten and won't perform as expected. We recommend disabling email tracking to ensure email links are not overwritten.

### Redirecting the user to a server-side endpoint[#](#redirecting-the-user-to-a-server-side-endpoint)

If you intend to use [Server-side rendering](https://supabase.com/docs/guides/auth/server-side-rendering), you might want the email link to redirect the user to a server-side endpoint to check if they are authenticated before returning the page. However, the default email link will redirect the user after verification to the redirect URL with the session in the query fragments. Since the session is returned in the query fragments by default, you won't be able to access it on the server-side.

You can customize the email link in the email template to redirect the user to a server-side endpoint successfully. For example:

```
1234<a  href="https://api.example.com/v1/authenticate?token_hash={{ .TokenHash }}&type=invite&redirect_to={{ .RedirectTo }}"  >Accept the invite</a>
```

When the user clicks on the link, the request will hit `https://api.example.com/v1/authenticate` and you can grab the `token_hash`, `type` and `redirect_to` query parameters from the URL. Then, you can call the [`verifyOtp`](https://supabase.com/docs/reference/javascript/auth-verifyotp) method to get back an authenticated session before redirecting the user back to the client. Since the `verifyOtp` method makes a `POST` request to Supabase Auth to verify the user, the session will be returned in the response body, which can be read by the server. For example:

```
12345678const { token_hash, type } = Object.fromEntries(new URLSearchParams(window.location.search))const {  data: { session },  error,} = await supabase.auth.verifyOtp({ token_hash, type })// subsequently redirect the user back to the client using the redirect_to param// ...
```

## Customization[#](#customization)

Supabase Auth makes use of [Go Templates](https://pkg.go.dev/text/template). This means it is possible to conditionally render information based on template properties.

### Send different email to early access users[#](#send-different-email-to-early-access-users)

Send a different email to users who signed up via an early access domain (`https://www.earlyaccess.trial.com`).

```
1234567891011121314{{ if eq .Data.Domain "https://www.example.com" }}<h1>Welcome to Our Database Service!</h1>  <p>Dear Developer,</p>  <p>Welcome to Billy, the scalable developer platform!</p>  <p>Best Regards,<br>Billy Team</p>{{ else if eq .Data.Domain "https://www.earlyaccess.trial.com" }}<h1>Welcome to Our Database Service!</h1>  <p>Dear Developer,</p>  <p>Welcome Billy, the scalable developer platform!</p>  <p> As an early access member, you have access to select features like Point To Space Restoration.</p>  <p>Best Regards,<br>Billy Team</p>{{ end }}
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/auth-email-templates.mdx)

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