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

5.  [Social Login (OAuth)](https://supabase.com/docs/guides/auth/social-login)

7.  [WorkOS](https://supabase.com/docs/guides/auth/social-login/auth-workos)

# 

SSO and Social Login with WorkOS

* * *

## Use Social Login with WorkOS[#](#use-social-login-with-workos)

### Step 1. Create a WorkOS organization[#](#step-1-create-a-workos-organization)

Log in to the WorkOS dashboard and visit the Organizations tab to create an organization. ![Create an Organization](https://supabase.com/docs/img/guides/auth-workos/workos-create-organization.png)

Alternatively, you can [create an organization via the WorkOS API](https://workos.com/docs/reference/organization/create).

## Step 2. Obtain your `Client ID` and `WORKOS_API_KEY` values[#](#step-2-obtain-your-client-id-and-workosapikey-values)

![Get your Environment's Client ID and Secret](https://supabase.com/docs/img/guides/auth-workos/workos-dashboard-get-client-id-and-key.png)

Visit the getting started page of the [WorkOS Dashboard](https://dashboard.workos.com/get-started). Copy the following values from the Quickstart panel:

-   `WORKOS_CLIENT_ID`
-   `WORKOS_API_KEY`

You must be signed in to see these values.

## Step 3. Add your WorkOS credentials to your Supabase project[#](#step-3-add-your-workos-credentials-to-your-supabase-project)

![Enter your WorkOS application details in your Supabase app's auth provider settings panel](https://supabase.com/docs/img/guides/auth-workos/supabase-workos-configuration.png)

1.  Go to your Supabase Project Dashboard.
2.  In the left sidebar, click the Authentication icon (near the top).
3.  Click on Providers under the Configuration section.
4.  Click on WorkOS from the accordion list to expand.
5.  Toggle the `WorkOS Enabled` switch to ON.
6.  Enter `https://api.workos.com` in the WorkOS URL field.
7.  Enter your WorkOS Client ID and WorkOS Client Secret saved in the previous step.
8.  Copy the `Callback URL (for OAuth)` value from the form and save it somewhere handy.
9.  Click Save.

## Step 4. Set your Supabase redirect URI in the WorkOS Dashboard[#](#step-4-set-your-supabase-redirect-uri-in-the-workos-dashboard)

Visit the WorkOS dashboard and click the redirects button in the left navigation panel.

On the redirects page, enter your Supabase project's `Callback URL (for OAuth)` which you saved in the previous step, as shown below:

![Set your Supbase project redirect URL in the WorkOS dashboard](https://supabase.com/docs/img/guides/auth-workos/workos-set-supabase-redirect.png)

## Step 5. Add login code to your client app[#](#step-5-add-login-code-to-your-client-app)

When a user signs in, call `signInWithOAuth` with `workos` as the provider.

```
123456789101112131415async function signInWithWorkOS() {  const { data, error } = await supabase.auth.signInWithOAuth({    provider: 'workos',    options: {      redirectTo: 'http://example.com/auth/v1/callback', // Make sure your redirect URL is configured in the Supabase Dashboard Auth settings      queryParams: {        connection: '<connection_id>',      },    },  })  if (data.url) {    redirect(data.url) // use the redirect API for your server or framework  }}
```

You can find your `connection_id` in the WorkOS dashboard under the Organizations tab. Select your organization and then click View connection.

Within your specified callback URL, you'll exchange the code for a logged-in user profile:

```
1234567891011121314151617181920212223242526272829import { NextResponse } from 'next/server'import { createClient } from '@/utils/supabase/server'export async function GET(request: Request) {  const { searchParams, origin } = new URL(request.url)  const code = searchParams.get('code')  // if "next" is in param, use it as the redirect URL  const next = searchParams.get('next') ?? '/'  if (code) {    const supabase = await createClient()    const { error } = await supabase.auth.exchangeCodeForSession(code)    if (!error) {      const forwardedHost = request.headers.get('x-forwarded-host') // original origin before load balancer      const isLocalEnv = process.env.NODE_ENV === 'development'      if (isLocalEnv) {        // we can be sure that there is no load balancer in between, so no need to watch for X-Forwarded-Host        return NextResponse.redirect(`${origin}${next}`)      } else if (forwardedHost) {        return NextResponse.redirect(`https://${forwardedHost}${next}`)      } else {        return NextResponse.redirect(`${origin}${next}`)      }    }  }  // return the user to an error page with instructions  return NextResponse.redirect(`${origin}/auth/auth-code-error`)}
```

## Resources[#](#resources)

-   [WorkOS Documentation](https://workos.com/docs/sso/guide)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/social-login/auth-workos.mdx)

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