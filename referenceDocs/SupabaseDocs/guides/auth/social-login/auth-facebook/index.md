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

7.  [Facebook](https://supabase.com/docs/guides/auth/social-login/auth-facebook)

# 

Login with Facebook

* * *

To enable Facebook Auth for your project, you need to set up a Facebook OAuth application and add the application credentials to your Supabase Dashboard.

## Overview[#](#overview)

Setting up Facebook logins for your application consists of 3 parts:

-   Create and configure a Facebook Application on the [Facebook Developers Site](https://developers.facebook.com)
-   Add your Facebook keys to your [Supabase Project](https://supabase.com/dashboard)
-   Add the login code to your [Supabase JS Client App](https://github.com/supabase/supabase-js)

## Access your Facebook Developer account[#](#access-your-facebook-developer-account)

-   Go to [developers.facebook.com](https://developers.facebook.com).
-   Click on `Log In` at the top right to log in.

![Facebook Developer Portal.](https://supabase.com/docs/img/guides/auth-facebook/facebook-portal.png)

## Create a Facebook app[#](#create-a-facebook-app)

-   Click on `My Apps` at the top right.
-   Click `Create App` near the top right.
-   Select your app type and click `Continue`.
-   Fill in your app information, then click `Create App`.
-   This should bring you to the screen: `Add Products to Your App`. (Alternatively you can click on `Add Product` in the left sidebar to get to this screen.)

The next step requires a callback URL, which looks like this: `https://<project-ref>.supabase.co/auth/v1/callback`

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   Click on the `Authentication` icon in the left sidebar
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **Facebook** from the accordion list to expand and you'll find your **Callback URL**, you can click `Copy` to copy it to the clipboard

For testing OAuth locally with the Supabase CLI see the [local development docs](https://supabase.com/docs/guides/cli/local-development#use-auth-locally).

## Set up Facebook login for your Facebook app[#](#set-up-facebook-login-for-your-facebook-app)

From the `Add Products to your App` screen:

-   Click `Setup` under `Facebook Login`
-   Skip the Quickstart screen, instead, in the left sidebar, click `Settings` under `Facebook Login`
-   Enter your callback URI under `Valid OAuth Redirect URIs` on the `Facebook Login Settings` page
-   Enter this in the `Valid OAuth Redirect URIs` box
-   Click `Save Changes` at the bottom right

Be aware that you have to set the right use case permissions to enable Third party applications to read the email address. To do so:

Under `Build Your App`, click on `Use Cases` screen. From there, do the following steps:

-   Click the Edit button in `Authentication and Account Creation` on the right side. This action will lead to the other page.
-   `public_profile` is set by default, so make sure it and `email` have status of **Ready for testing** in the redirected page.
-   If not, click the **Add** button in email on right side.

## Copy your Facebook app ID and secret[#](#copy-your-facebook-app-id-and-secret)

-   Click `Settings / Basic` in the left sidebar
-   Copy your App ID from the top of the `Basic Settings` page
-   Under `App Secret` click `Show` then copy your secret
-   Make sure all required fields are completed on this screen.

## Enter your Facebook app ID and secret into your Supabase project[#](#enter-your-facebook-app-id-and-secret-into-your-supabase-project)

-   Go to your [Supabase Project Dashboard](https://supabase.com/dashboard)
-   In the left sidebar, click the `Authentication` icon (near the top)
-   Click on [`Providers`](https://supabase.com/dashboard/project/_/auth/providers) under the Configuration section
-   Click on **Facebook** from the accordion list to expand and turn **Facebook Enabled** to ON
-   Enter your **Facebook Client ID** and **Facebook Client Secret** saved in the previous step
-   Click `Save`

## Add login code to your client app[#](#add-login-code-to-your-client-app)

JavaScriptFlutterSwiftKotlin

Make sure you're using the right `supabase` client in the following code.

If you're not using Server-Side Rendering or cookie-based Auth, you can directly use the `createClient` from `@supabase/supabase-js`. If you're using Server-Side Rendering, see the [Server-Side Auth guide](https://supabase.com/docs/guides/auth/server-side/creating-a-client) for instructions on creating your Supabase client.

When your user signs in, call [`signInWithOAuth()`](https://supabase.com/docs/reference/javascript/auth-signinwithoauth) with `facebook` as the `provider`:

```
12345async function signInWithFacebook() {  const { data, error } = await supabase.auth.signInWithOAuth({    provider: 'facebook',  })}
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

JavaScriptFlutterSwiftKotlin

When your user signs out, call [signOut()](https://supabase.com/docs/reference/javascript/auth-signout) to remove them from the browser session and any objects from localStorage:

```
123async function signOut() {  const { error } = await supabase.auth.signOut()}
```

Now, you should be able to login with Facebook and alert you to `Submit for Login Review` when users try to sign into your app. Follow the instructions there to make your app go live for full features and products. You can read more about App Review [here](https://developers.facebook.com/docs/app-review/).

## Resources[#](#resources)

-   [Supabase - Get started for free](https://supabase.com)
-   [Supabase JS Client](https://github.com/supabase/supabase-js)
-   [Facebook Developers Dashboard](https://developers.facebook.com/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/social-login/auth-facebook.mdx)

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