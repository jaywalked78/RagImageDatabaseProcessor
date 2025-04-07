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

5.  [Mobile Deep Linking](https://supabase.com/docs/guides/auth/native-mobile-deep-linking)

# 

Native Mobile Deep Linking

## 

Set up Deep Linking for mobile applications.

* * *

Many Auth methods involve a redirect to your app. For example:

-   Signup confirmation emails, Magic Link signins, and password reset emails contain a link that redirects to your app.
-   In OAuth signins, an automatic redirect occurs to your app.

With Deep Linking, you can configure this redirect to open a specific page. This is necessary if, for example, you need to display a form for [password reset](https://supabase.com/docs/guides/auth/passwords#resetting-a-users-password-forgot-password), or to manually exchange a token hash.

## Setting up deep linking[#](#setting-up-deep-linking)

Expo React NativeFlutterSwiftAndroid Kotlin

To link to your development build or standalone app, you need to specify a custom URL scheme for your app. You can register a scheme in your app config (app.json, app.config.js) by adding a string under the `scheme` key:

```
12345{  "expo": {    "scheme": "com.supabase"  }}
```

In your project's [auth settings](https://supabase.com/dashboard/project/_/auth/url-configuration) add the redirect URL, e.g. `com.supabase://**`.

Finally, implement the OAuth and linking handlers. See the [supabase-js reference](https://supabase.com/docs/reference/javascript/initializing?example=react-native-options-async-storage) for instructions on initializing the supabase-js client in React Native.

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071import { Button } from "react-native";import { makeRedirectUri } from "expo-auth-session";import * as QueryParams from "expo-auth-session/build/QueryParams";import * as WebBrowser from "expo-web-browser";import * as Linking from "expo-linking";import { supabase } from "app/utils/supabase";WebBrowser.maybeCompleteAuthSession(); // required for web onlyconst redirectTo = makeRedirectUri();const createSessionFromUrl = async (url: string) => {  const { params, errorCode } = QueryParams.getQueryParams(url);  if (errorCode) throw new Error(errorCode);  const { access_token, refresh_token } = params;  if (!access_token) return;  const { data, error } = await supabase.auth.setSession({    access_token,    refresh_token,  });  if (error) throw error;  return data.session;};const performOAuth = async () => {  const { data, error } = await supabase.auth.signInWithOAuth({    provider: "github",    options: {      redirectTo,      skipBrowserRedirect: true,    },  });  if (error) throw error;  const res = await WebBrowser.openAuthSessionAsync(    data?.url ?? "",    redirectTo  );  if (res.type === "success") {    const { url } = res;    await createSessionFromUrl(url);  }};const sendMagicLink = async () => {  const { error } = await supabase.auth.signInWithOtp({    email: "valid.email@supabase.io",    options: {      emailRedirectTo: redirectTo,    },  });  if (error) throw error;  // Email sent.};export default function Auth() {  // Handle linking into app from email app.  const url = Linking.useURL();  if (url) createSessionFromUrl(url);  return (    <>      <Button onPress={performOAuth} title="Sign in with Github" />      <Button onPress={sendMagicLink} title="Send Magic Link" />    </>  );}
```

For the best user experience it is recommended to use universal links which require a more elaborate setup. You can find the detailed setup instructions in the [Expo docs](https://docs.expo.dev/guides/deep-linking/).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/native-mobile-deep-linking.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F8TZ6O1C8ujE%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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