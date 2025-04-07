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

7.  [LinkedIn](https://supabase.com/docs/guides/auth/social-login/auth-linkedin)

# 

Login with LinkedIn

* * *

To enable LinkedIn Auth for your project, you need to set up a LinkedIn OAuth application and add the application credentials to your Supabase Dashboard.

## Overview[#](#overview)

Setting up LinkedIn logins for your application consists of 3 parts:

-   Create and configure a LinkedIn Project and App on the [LinkedIn Developer Dashboard](https://www.linkedin.com/developers/apps).
-   Add your _LinkedIn (OIDC)_ `client_id` and `client_secret` to your [Supabase Project](https://supabase.com/dashboard).
-   Add the login code to your [Supabase JS Client App](https://github.com/supabase/supabase-js).

## Access your LinkedIn Developer account[#](#access-your-linkedin-developer-account)

-   Go to [LinkedIn Developer Dashboard](https://www.linkedin.com/developers/apps).
-   Log in (if necessary.)

![LinkedIn Developer Portal](https://supabase.com/docs/img/guides/auth-linkedin/linkedin_developers_page.png)

## Find your callback URL[#](#find-your-callback-url)

The next step requires a callback URL, which looks like this: `https://<project-ref>.supabase.co/auth/v1/callback`

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   Click on the `Authentication` icon in the left sidebar
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **LinkedIn** from the accordion list to expand and you'll find your **Callback URL**, you can click `Copy` to copy it to the clipboard

For testing OAuth locally with the Supabase CLI see the [local development docs](https://supabase.com/docs/guides/cli/local-development#use-auth-locally).

## Create a LinkedIn OAuth app[#](#create-a-linkedin-oauth-app)

-   Go to [LinkedIn Developer Dashboard](https://www.linkedin.com/developers/apps).
-   Click on `Create App` at the top right
-   Enter your `LinkedIn Page` and `App Logo`
-   Save your app
-   Click `Products` from the top menu
-   Look for `Sign In with LinkedIn using OpenID Connect` and click on Request Access
-   Click `Auth` from the top menu
-   Add your `Redirect URL` to the `Authorized Redirect URLs for your app` section
-   Copy and save your newly-generated `Client ID`
-   Copy and save your newly-generated `Client Secret`

Ensure that the appropriate scopes have been added under OAuth 2.0 Scopes at the bottom of the `Auth` screen.

![Required OAuth 2.0 Scopes](https://supabase.com/docs/img/guides/auth-linkedin/oauth-scopes.png)

## Enter your LinkedIn (OIDC) credentials into your Supabase project[#](#enter-your-linkedin-oidc-credentials-into-your-supabase-project)

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   In the left sidebar, click the `Authentication` icon (near the top)
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **LinkedIn (OIDC)** from the accordion list to expand and turn **LinkedIn (OIDC) Enabled** to ON
-   Enter your **LinkedIn (OIDC) Client ID** and **LinkedIn (OIDC) Client Secret** saved in the previous step
-   Click `Save`

## Add login code to your client app[#](#add-login-code-to-your-client-app)

JavaScriptFlutterKotlin

Make sure you're using the right `supabase` client in the following code.

If you're not using Server-Side Rendering or cookie-based Auth, you can directly use the `createClient` from `@supabase/supabase-js`. If you're using Server-Side Rendering, see the [Server-Side Auth guide](https://supabase.com/docs/guides/auth/server-side/creating-a-client) for instructions on creating your Supabase client.

When your user signs in, call [`signInWithOAuth()`](https://supabase.com/docs/reference/javascript/auth-signinwithoauth) with `linkedin_oidc` as the `provider`:

```
12345async function signInWithLinkedIn() {  const { data, error } = await supabase.auth.signInWithOAuth({    provider: 'linkedin_oidc',  })}
```

For a PKCE flow, for example in Server-Side Auth, you need an extra step to handle the code exchange. When calling `signInWithOAuth`, provide a `redirectTo` URL which points to a callback route. This redirect URL should be added to your [redirect allow list](https://supabase.com/docs/guides/auth/redirect-urls).

ClientServer

In the browser, `signInWithOAuth` automatically redirects to the OAuth provider's authentication endpoint, which then redirects to your endpoint.

```
123456await supabase.auth.signInWithOAuth({  provider,  options: {    redirectTo: `http://example.com/auth/callback`,  },})
```

At the callback endpoint, handle the code exchange to save the user session.

Next.jsSvelteKitAstroRemixExpress

Create a new file at `app/auth/callback/route.ts` and populate with the following:

```
123456789101112131415161718192021222324252627282930import { NextResponse } from 'next/server'// The client you created from the Server-Side Auth instructionsimport { createClient } from '@/utils/supabase/server'export async function GET(request: Request) {  const { searchParams, origin } = new URL(request.url)  const code = searchParams.get('code')  // if "next" is in param, use it as the redirect URL  const next = searchParams.get('next') ?? '/'  if (code) {    const supabase = await createClient()    const { error } = await supabase.auth.exchangeCodeForSession(code)    if (!error) {      const forwardedHost = request.headers.get('x-forwarded-host') // original origin before load balancer      const isLocalEnv = process.env.NODE_ENV === 'development'      if (isLocalEnv) {        // we can be sure that there is no load balancer in between, so no need to watch for X-Forwarded-Host        return NextResponse.redirect(`${origin}${next}`)      } else if (forwardedHost) {        return NextResponse.redirect(`https://${forwardedHost}${next}`)      } else {        return NextResponse.redirect(`${origin}${next}`)      }    }  }  // return the user to an error page with instructions  return NextResponse.redirect(`${origin}/auth/auth-code-error`)}
```

JavaScriptFlutterKotlin

When your user signs out, call [signOut()](https://supabase.com/docs/reference/javascript/auth-signout) to remove them from the browser session and any objects from localStorage:

```
123async function signOut() {  const { error } = await supabase.auth.signOut()}
```

## LinkedIn Open ID Connect (OIDC)[#](#linkedin-open-id-connect-oidc)

We will be replacing the _LinkedIn_ provider with a new _LinkedIn (OIDC)_ provider to support recent changes to the LinkedIn [OAuth APIs](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?context=linkedin%2Fcontext&tabs=HTTPS1). The new provider utilizes the [Open ID Connect standard](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2#validating-id-tokens). In view of this change, we have disabled edits on the _LinkedIn_ provider and will be removing it effective 4th January 2024. Developers with LinkedIn OAuth Applications created prior to 1st August 2023 should create a new OAuth application [via the steps outlined above](https://supabase.com/docs/guides/auth/social-login/auth-linkedin#create-a-linkedin-oauth-app) and migrate their credentials from the _LinkedIn_ provider to the _LinkedIn (OIDC)_ provider. Alternatively, you can also head to the `Products` section and add the newly release`Sign In with LinkedIn using OpenID Connect` to your existing OAuth application.

Developers using the Supabase CLI to test their LinkedIn OAuth application should also update their `config.toml` to make use of the new provider:

```
1234[auth.external.linkedin_oidc]enabled = trueclient_id = ...secret = ...
```

Do reach out to support if you have any concerns around this change.

## Resources[#](#resources)

-   [Supabase - Get started for free](https://supabase.com)
-   [Supabase JS Client](https://github.com/supabase/supabase-js)
-   [LinkedIn Developer Dashboard](https://api.LinkedIn.com/apps)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/social-login/auth-linkedin.mdx)

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