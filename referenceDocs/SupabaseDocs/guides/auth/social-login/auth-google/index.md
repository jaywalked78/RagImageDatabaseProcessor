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

7.  [Google](https://supabase.com/docs/guides/auth/social-login/auth-google)

# 

Login with Google

* * *

Supabase Auth supports Sign in with Google for the web, native Android applications, and Chrome extensions.

## Prerequisites[#](#prerequisites)

-   A Google Cloud project. Go to the [Google Cloud Platform](https://console.cloud.google.com/home/dashboard) and create a new project if necessary.

## Configuration[#](#configuration)

To support Sign In with Google, you need to configure the Google provider for your Supabase project.

WebExpo React NativeFlutterSwiftAndroid (Kotlin)Chrome Extensions

For web applications, you can set up your signin button two different ways:

-   Use your own [application code](#application-code) for the button.
-   Use [Google's pre-built sign-in or One Tap flows](#google-pre-built).

### Application code configuration[#](#application-code-configuration)

To use your own application code:

1.  In the Google Cloud console, go to the [Consent Screen configuration page](https://console.cloud.google.com/apis/credentials/consent). The consent screen is the view shown to your users when they consent to signing in to your app.
    
2.  Under **Authorized domains**, add your Supabase project's domain, which has the form `<PROJECT_ID>.supabase.co`.
    
3.  Configure the following non-sensitive scopes:
    
    -   `.../auth/userinfo.email`
    -   `...auth/userinfo.profile`
    -   `openid`
4.  Go to the [API Credentials page](https://console.cloud.google.com/apis/credentials).
    
5.  Click `Create credentials` and choose `OAuth Client ID`.
    
6.  For application type, choose `Web application`.
    
7.  Under **Authorized JavaScript origins**, add your site URL.
    
8.  Under **Authorized redirect URLs**, enter the callback URL from the [Supabase dashboard](https://supabase.com/dashboard/project/_/auth/providers). Expand the Google Auth Provider section to display it.
    
    The redirect URL is visible to your users. You can customize it by configuring [custom domains](https://supabase.com/docs/guides/platform/custom-domains).
    
9.  When you finish configuring your credentials, you will be shown your client ID and secret. Add these to the [Google Auth Provider section of the Supabase Dashboard](https://supabase.com/dashboard/project/_/auth/providers).
    
    In local development, you can add the client ID and secret to your `config.toml` file.
    

### Google pre-built configuration[#](#google-pre-built-configuration)

To use Google's pre-built signin buttons:

1.  In the Google Cloud console, go to the [Consent Screen configuration page](https://console.cloud.google.com/apis/credentials/consent). The consent screen is the view shown to your users when they consent to signing in to your app.
2.  Configure the screen to your liking, making sure you add links to your app's privacy policy and terms of service.
3.  Go to the [API Credentials page](https://console.cloud.google.com/apis/credentials).
4.  Click `Create credentials` and choose `OAuth Client ID`.
5.  For application type, choose `Web application`.
6.  Under **Authorized JavaScript origins** and **Authorized redirect URLs**, add your site URL. This is the URL of the website where the signin button will appear, _not_ your Supabase project domain. If you're testing in localhost, ensure that you have `http://localhost` set in the **Authorized JavaScript origins** section as well. This is important when integrating with Google One-Tap to ensure you can use it locally.
7.  When you finish configuring your credentials, you will be shown your client ID. Add this to the **Client IDs** field in the [Google Auth Provider section of the Supabase Dashboard](https://supabase.com/dashboard/project/_/auth/providers). Leave the OAuth client ID and secret blank. You don't need them when using Google's pre-built approach.

## Signing users in[#](#signing-users-in)

WebExpo React NativeFlutterAndroid (Kotlin)Chrome Extensions

### Application code[#](#application-code)

To use your own application code for the signin button, call the `signInWithOAuth` method (or the equivalent for your language).

Make sure you're using the right `supabase` client in the following code.

If you're not using Server-Side Rendering or cookie-based Auth, you can directly use the `createClient` from `@supabase/supabase-js`. If you're using Server-Side Rendering, see the [Server-Side Auth guide](https://supabase.com/docs/guides/auth/server-side/creating-a-client) for instructions on creating your Supabase client.

```
123supabase.auth.signInWithOAuth({  provider: 'google',})
```

For an implicit flow, that's all you need to do. The user will be taken to Google's consent screen, and finally redirected to your app with an access and refresh token pair representing their session.

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

After a successful code exchange, the user's session will be saved to cookies.

### Saving Google tokens[#](#saving-google-tokens)

The tokens saved by your application are the Supabase Auth tokens. Your app might additionally need the Google OAuth 2.0 tokens to access Google services on the user's behalf.

On initial login, you can extract the `provider_token` from the session and store it in a secure storage medium. The session is available in the returned data from `signInWithOAuth` (implicit flow) and `exchangeCodeForSession` (PKCE flow).

Google does not send out a refresh token by default, so you will need to pass parameters like these to `signInWithOAuth()` in order to extract the `provider_refresh_token`:

```
123456789const { data, error } = await supabase.auth.signInWithOAuth({  provider: 'google',  options: {    queryParams: {      access_type: 'offline',      prompt: 'consent',    },  },})
```

### Google pre-built[#](#google-pre-built)

Most web apps and websites can utilize Google's [personalized sign-in buttons](https://developers.google.com/identity/gsi/web/guides/personalized-button), [One Tap](https://developers.google.com/identity/gsi/web/guides/features) or [automatic sign-in](https://developers.google.com/identity/gsi/web/guides/automatic-sign-in-sign-out) for the best user experience.

1.  Load the Google client library in your app by including the third-party script:
    
    ```
    1<script src="https://accounts.google.com/gsi/client" async></script>
    ```
    
2.  Use the [HTML Code Generator](https://developers.google.com/identity/gsi/web/tools/configurator) to customize the look, feel, features and behavior of the Sign in with Google button.
    
3.  Pick the _Swap to JavaScript callback_ option, and input the name of your callback function. This function will receive a [`CredentialResponse`](https://developers.google.com/identity/gsi/web/reference/js-reference#CredentialResponse) when sign in completes.
    
    To make your app compatible with Chrome's third-party-cookie phase-out, make sure to set `data-use_fedcm_for_prompt` to `true`.
    
    Your final HTML code might look something like this:
    
    ```
    123456789101112131415161718192021<div  id="g_id_onload"  data-client_id="<client ID>"  data-context="signin"  data-ux_mode="popup"  data-callback="handleSignInWithGoogle"  data-nonce=""  data-auto_select="true"  data-itp_support="true"  data-use_fedcm_for_prompt="true"></div><div  class="g_id_signin"  data-type="standard"  data-shape="pill"  data-theme="outline"  data-text="signin_with"  data-size="large"  data-logo_alignment="left"></div>
    ```
    
4.  Create a `handleSignInWithGoogle` function that takes the `CredentialResponse` and passes the included token to Supabase. The function needs to be available in the global scope for Google's code to find it.
    
    ```
    123456async function handleSignInWithGoogle(response) {  const { data, error } = await supabase.auth.signInWithIdToken({    provider: 'google',    token: response.credential,  })}
    ```
    
5.  _(Optional)_ Configure a nonce. The use of a nonce is recommended for extra security, but optional. The nonce should be generated randomly each time, and it must be provided in both the `data-nonce` attribute of the HTML code and the options of the callback function.
    
    ```
    1234567async function handleSignInWithGoogle(response) {  const { data, error } = await supabase.auth.signInWithIdToken({    provider: 'google',    token: response.credential,    nonce: '<NONCE>',  })}
    ```
    
    Note that the nonce should be the same in both places, but because Supabase Auth expects the provider to hash it (SHA-256, hexadecimal representation), you need to provide a hashed version to Google and a non-hashed version to `signInWithIdToken`.
    
    You can get both versions by using the in-built `crypto` library:
    
    ```
    123456789101112// Adapted from https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest#converting_a_digest_to_a_hex_stringconst nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(32))))const encoder = new TextEncoder()const encodedNonce = encoder.encode(nonce)crypto.subtle.digest('SHA-256', encodedNonce).then((hashBuffer) => {  const hashArray = Array.from(new Uint8Array(hashBuffer))  const hashedNonce = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')})// Use 'hashedNonce' when making the authentication request to Google// Use 'nonce' when invoking the supabase.auth.signInWithIdToken() method
    ```
    

### One-tap with Next.js[#](#one-tap-with-nextjs)

If you're integrating Google One-Tap with your Next.js application, you can refer to the example below to get started:

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283'use client'import Script from 'next/script'import { createClient } from '@/utils/supabase/client'import { CredentialResponse } from 'google-one-tap'import { useRouter } from 'next/navigation'import { useEffect } from 'react'const OneTapComponent = () => {  const supabase = createClient()  const router = useRouter()  // generate nonce to use for google id token sign-in  const generateNonce = async (): Promise<string[]> => {    const nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(32))))    const encoder = new TextEncoder()    const encodedNonce = encoder.encode(nonce)    const hashBuffer = await crypto.subtle.digest('SHA-256', encodedNonce)    const hashArray = Array.from(new Uint8Array(hashBuffer))    const hashedNonce = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')    return [nonce, hashedNonce]  }  useEffect(() => {    const initializeGoogleOneTap = () => {      console.log('Initializing Google One Tap')      window.addEventListener('load', async () => {        const [nonce, hashedNonce] = await generateNonce()        console.log('Nonce: ', nonce, hashedNonce)        // check if there's already an existing session before initializing the one-tap UI        const { data, error } = await supabase.auth.getSession()        if (error) {          console.error('Error getting session', error)        }        if (data.session) {          router.push('/')          return        }        /* global google */        google.accounts.id.initialize({          client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,          callback: async (response: CredentialResponse) => {            try {              // send id token returned in response.credential to supabase              const { data, error } = await supabase.auth.signInWithIdToken({                provider: 'google',                token: response.credential,                nonce,              })              if (error) throw error              console.log('Session data: ', data)              console.log('Successfully logged in with Google One Tap')              // redirect to protected page              router.push('/')            } catch (error) {              console.error('Error logging in with Google One Tap', error)            }          },          nonce: hashedNonce,          // with chrome's removal of third-party cookiesm, we need to use FedCM instead (https://developers.google.com/identity/gsi/web/guides/fedcm-migration)          use_fedcm_for_prompt: true,        })        google.accounts.id.prompt() // Display the One Tap UI      })    }    initializeGoogleOneTap()    return () => window.removeEventListener('load', initializeGoogleOneTap)  }, [])  return (    <>      <Script src="https://accounts.google.com/gsi/client" />      <div id="oneTap" className="fixed top-0 right-0 z-[100]" />    </>  )}export default OneTapComponent
```

## Google consent screen[#](#google-consent-screen)

![Google Consent Screen](https://supabase.com/docs/img/guides/auth-google/auth-google-consent-screen.png)

By default, the Google consent screen shows the root domain of the callback URL, where Google will send the authentication response. With Supabase Auth, it is your Supabase project's domain `(https://<your-project-ref>.supabase.co)`.

If that is not preferable, you can use a [Custom Domain](https://supabase.com/docs/guides/platform/custom-domains) with your Supabase project. You can use it as your project's domain when creating the Supabase client in your application and initiating the authentication flow. It will then show up in the Google consent screen. If you want your app name and the logo on the consent screen, [you must submit your app to Google for verification](https://support.google.com/cloud/answer/10311615).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/social-login/auth-google.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FvojHmGUGUGc%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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