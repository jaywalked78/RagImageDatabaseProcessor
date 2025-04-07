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

7.  [Bitbucket](https://supabase.com/docs/guides/auth/social-login/auth-bitbucket)

# 

Login with Bitbucket

* * *

To enable Bitbucket Auth for your project, you need to set up a Bitbucket OAuth application and add the application credentials to your Supabase Dashboard.

## Overview[#](#overview)

Setting up Bitbucket logins for your application consists of 3 parts:

-   Create and configure a Bitbucket OAuth Consumer on [Bitbucket](https://bitbucket.org)
-   Add your Bitbucket OAuth Consumer keys to your [Supabase Project](https://supabase.com/dashboard)
-   Add the login code to your [Supabase JS Client App](https://github.com/supabase/supabase-js)

## Access your Bitbucket account[#](#access-your-bitbucket-account)

-   Go to [bitbucket.org](https://bitbucket.org/).
-   Click on `Login` at the top right to log in.

![Bitbucket Developer Portal.](https://supabase.com/docs/img/guides/auth-bitbucket/bitbucket-portal.png)

## Find your callback URL[#](#find-your-callback-url)

The next step requires a callback URL, which looks like this: `https://<project-ref>.supabase.co/auth/v1/callback`

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   Click on the `Authentication` icon in the left sidebar
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **Bitbucket** from the accordion list to expand and you'll find your **Callback URL**, you can click `Copy` to copy it to the clipboard

For testing OAuth locally with the Supabase CLI see the [local development docs](https://supabase.com/docs/guides/cli/local-development#use-auth-locally).

## Create a Bitbucket OAuth app[#](#create-a-bitbucket-oauth-app)

-   Click on your profile icon at the bottom left
-   Click on `All Workspaces`
-   Select a workspace and click on it to select it
-   Click on `Settings` on the left
-   Click on `OAuth consumers` on the left under `Apps and Features` (near the bottom)
-   Click `Add Consumer` at the top
-   Enter the name of your app under `Name`
-   In `Callback URL`, type the callback URL of your app
-   Check the permissions you need (Email, Read should be enough)
-   Click `Save` at the bottom
-   Click on your app name (the name of your new OAuth Consumer)
-   Copy your `Key` (`client_key`) and `Secret` (`client_secret`) codes

## Add your Bitbucket credentials into your Supabase project[#](#add-your-bitbucket-credentials-into-your-supabase-project)

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   In the left sidebar, click the `Authentication` icon (near the top)
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **BitBucket** from the accordion list to expand and turn **BitBucket Enabled** to ON
-   Enter your **BitBucket Client ID** and **BitBucket Client Secret** saved in the previous step
-   Click `Save`

## Add login code to your client app[#](#add-login-code-to-your-client-app)

JavaScriptFlutterKotlin

Make sure you're using the right `supabase` client in the following code.

If you're not using Server-Side Rendering or cookie-based Auth, you can directly use the `createClient` from `@supabase/supabase-js`. If you're using Server-Side Rendering, see the [Server-Side Auth guide](https://supabase.com/docs/guides/auth/server-side/creating-a-client) for instructions on creating your Supabase client.

When your user signs in, call [`signInWithOAuth()`](https://supabase.com/docs/reference/javascript/auth-signinwithoauth) with `bitbucket` as the `provider`:

```
12345async function signInWithBitbucket() {  const { data, error } = await supabase.auth.signInWithOAuth({    provider: 'bitbucket',  })}
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

## Resources[#](#resources)

-   [Supabase - Get started for free](https://supabase.com)
-   [Supabase JS Client](https://github.com/supabase/supabase-js)
-   [Bitbucket Account](https://bitbucket.org)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/social-login/auth-bitbucket.mdx)

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