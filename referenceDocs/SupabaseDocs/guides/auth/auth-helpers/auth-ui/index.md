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

3.  Auth UI

5.  [Auth UI (Deprecated)](https://supabase.com/docs/guides/auth/auth-helpers/auth-ui)

# 

Auth UI

* * *

As of 7th Feb 2024, [this repository](https://github.com/supabase-community/auth-ui) is no longer maintained by the Supabase Team. At the moment, the team does not have capacity to give the expected level of care to this repository. We may revisit Auth UI in the future but regrettably have to leave it on hold for now as we focus on other priorities such as improving the Server-Side Rendering (SSR) package and advanced Auth primitives.

Auth UI is a pre-built React component for authenticating users. It supports custom themes and extensible styles to match your brand and aesthetic.

## Set up Auth UI[#](#set-up-auth-ui)

Install the latest version of [supabase-js](https://supabase.com/docs/reference/javascript) and the Auth UI package:

```
1npm install @supabase/supabase-js @supabase/auth-ui-react @supabase/auth-ui-shared
```

### Import the Auth component[#](#import-the-auth-component)

Pass `supabaseClient` from `@supabase/supabase-js` as a prop to the component.

```
123456import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => <Auth supabaseClient={supabase} />
```

This renders the Auth component without any styling. We recommend using one of the predefined themes to style the UI. Import the theme you want to use and pass it to the `appearance.theme` prop.

```
123456789101112131415161718import { Auth } from '@supabase/auth-ui-react'import {  // Import predefined theme  ThemeSupa,} from '@supabase/auth-ui-shared'const supabase = createClient(  '<INSERT PROJECT URL>',  '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    {/* Apply predefined theme */}    appearance={{ theme: ThemeSupa }}  />)
```

### Social providers[#](#social-providers)

The Auth component also supports login with [official social providers](https://supabase.com/docs/guides/auth#providers).

```
12345678910111213import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'import { ThemeSupa } from '@supabase/auth-ui-shared'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    appearance={{ theme: ThemeSupa }}    providers={['google', 'facebook', 'twitter']}  />)
```

### Options[#](#options)

Options are available via `queryParams`:

```
12345678910<Auth  supabaseClient={supabase}  providers={['google']}  queryParams={{    access_type: 'offline',    prompt: 'consent',    hd: 'domain.com',  }}  onlyThirdPartyProviders/>
```

### Provider scopes[#](#provider-scopes)

Provider Scopes can be requested through `providerScope`;

```
123456789101112<Auth  supabaseClient={supabase}  providers={['google']}  queryParams={{    access_type: 'offline',    prompt: 'consent',    hd: 'domain.com',  }}  providerScopes={{    google: 'https://www.googleapis.com/auth/calendar.readonly',  }}/>
```

### Supported views[#](#supported-views)

The Auth component is currently shipped with the following views:

-   [Email Login](https://supabase.com/docs/guides/auth/auth-email)
-   [Magic Link login](https://supabase.com/docs/guides/auth/auth-magic-link)
-   [Social Login](https://supabase.com/docs/guides/auth/social-login)
-   Update password
-   Forgotten password

We are planning on adding more views in the future. Follow along on that [repo](https://github.com/supabase/auth-ui).

## Customization[#](#customization)

There are several ways to customize Auth UI:

-   Use one of the [predefined themes](#predefined-themes) that comes with Auth UI
-   Extend a theme by [overriding the variable tokens](#override-themes) in a theme
-   [Create your own theme](#create-theme)
-   [Use your own CSS classes](#custom-css-classes)
-   [Use inline styles](#custom-inline-styles)
-   [Use your own labels](#custom-labels)

### Predefined themes[#](#predefined-themes)

Auth UI comes with several themes to customize the appearance. Each predefined theme comes with at least two variations, a `default` variation, and a `dark` variation. You can switch between these themes using the `theme` prop. Import the theme you want to use and pass it to the `appearance.theme` prop.

```
12345678910111213141516import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'import { ThemeSupa } from '@supabase/auth-ui-shared'const supabase = createClient(  '<INSERT PROJECT URL>',  '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    {/* Apply predefined theme */}    appearance={{ theme: ThemeSupa }}  />)
```

Currently there is only one predefined theme available, but we plan to add more.

### Switch theme variations[#](#switch-theme-variations)

Auth UI comes with two theme variations: `default` and `dark`. You can switch between these themes with the `theme` prop.

```
1234567891011121314151617import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'import { ThemeSupa } from '@supabase/auth-ui-shared'const supabase = createClient(  '<INSERT PROJECT URL>',  '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    appearance={{ theme: ThemeSupa }}    {/* Set theme to dark */}    theme="dark"  />)
```

If you don't pass a value to `theme` it uses the `"default"` theme. You can pass `"dark"` to the theme prop to switch to the `dark` theme. If your theme has other variations, use the name of the variation in this prop.

### Override themes[#](#override-themes)

Auth UI themes can be overridden using variable tokens. See the [list of variable tokens](https://github.com/supabase/auth-ui/blob/main/packages/shared/src/theming/Themes.ts).

```
12345678910111213141516171819202122import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'import { ThemeSupa } from '@supabase/auth-ui-shared'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    appearance={{      theme: ThemeSupa,      variables: {        default: {          colors: {            brand: 'red',            brandAccent: 'darkred',          },        },      },    }}  />)
```

If you created your own theme, you may not need to override any of them.

### Create your own theme [#](#create-theme)

You can create your own theme by following the same structure within a `appearance.theme` property. See the list of [tokens within a theme](https://github.com/supabase/auth-ui/blob/main/packages/shared/src/theming/Themes.ts).

```
12345678910111213141516171819202122232425262728293031323334353637383940import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const customTheme = {  default: {    colors: {      brand: 'hsl(153 60.0% 53.0%)',      brandAccent: 'hsl(154 54.8% 45.1%)',      brandButtonText: 'white',      // ..    },  },  dark: {    colors: {      brandButtonText: 'white',      defaultButtonBackground: '#2e2e2e',      defaultButtonBackgroundHover: '#3e3e3e',      //..    },  },  // You can also add more theme variations with different names.  evenDarker: {    colors: {      brandButtonText: 'white',      defaultButtonBackground: '#1e1e1e',      defaultButtonBackgroundHover: '#2e2e2e',      //..    },  },}const App = () => (  <Auth    supabaseClient={supabase}    theme="default" // can also be "dark" or "evenDarker"    appearance={{ theme: customTheme }}  />)
```

You can switch between different variations of your theme with the ["theme" prop](#switch-theme-variations).

### Custom CSS classes [#](#custom-css-classes)

You can use custom CSS classes for the following elements: `"button"`, `"container"`, `"anchor"`, `"divider"`, `"label"`, `"input"`, `"loader"`, `"message"`.

```
1234567891011121314151617181920import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    appearance={{      // If you want to extend the default styles instead of overriding it, set this to true      extend: false,      // Your custom classes      className: {        anchor: 'my-awesome-anchor',        button: 'my-awesome-button',        //..      },    }}  />)
```

### Custom inline CSS [#](#custom-inline-styles)

You can use custom CSS inline styles for the following elements: `"button"`, `"container"`, `"anchor"`, `"divider"`, `"label"`, `"input"`, `"loader"`, `"message"`.

```
1234567891011121314151617import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    appearance={{      style: {        button: { background: 'red', color: 'white' },        anchor: { color: 'blue' },        //..      },    }}  />)
```

### Custom labels [#](#custom-labels)

You can use custom labels with `localization.variables` like so:

```
123456789101112131415161718import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => (  <Auth    supabaseClient={supabase}    localization={{      variables: {        sign_in: {          email_label: 'Your email address',          password_label: 'Your strong password',        },      },    }}  />)
```

A full list of the available variables is below:

Sign UpSign InMagic LinkForgotten PasswordUpdate PasswordVerify OTP

| Label Tag | Default Label |
| --- | --- |
| `email_label` | Email address |
| `password_label` | Create a Password |
| `email_input_placeholder` | Your email address |
| `password_input_placeholder` | Your password |
| `button_label` | Sign up |
| `loading_button_label` | Signing up ... |
| `social_provider_text` | Sign in with `{{provider}}` |
| `link_text` | Don't have an account? Sign up |
| `confirmation_text` | Check your email for the confirmation link |

Currently, translating error messages (e.g. "Invalid credentials") is not supported. Check [related issue.](https://github.com/supabase/auth-ui/issues/86)

### Hiding links [#](#hiding-links)

You can hide links by setting the `showLinks` prop to `false`

```
123456import { createClient } from '@supabase/supabase-js'import { Auth } from '@supabase/auth-ui-react'const supabase = createClient('<INSERT PROJECT URL>', '<INSERT PROJECT ANON API KEY>')const App = () => <Auth supabaseClient={supabase} showLinks={false} />
```

Setting `showLinks` to `false` will hide the following links:

-   Don't have an account? Sign up
-   Already have an account? Sign in
-   Send a magic link email
-   Forgot your password?

### Sign in and sign up views[#](#sign-in-and-sign-up-views)

Add `sign_in` or `sign_up` views with the `view` prop:

```
1234<Auth  supabaseClient={supabase}  view="sign_up"/>
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/auth-helpers/auth-ui.mdx)

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