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

5.  [Flutter Auth UI](https://supabase.com/docs/guides/auth/auth-helpers/flutter-auth-ui)

# 

Flutter Auth UI

* * *

Flutter Auth UI is a Flutter package containing pre-built widgets for authenticating users. It is unstyled and can match your brand and aesthetic.

![Flutter Auth UI](https://raw.githubusercontent.com/supabase-community/flutter-auth-ui/main/screenshots/supabase_auth_ui.png)

## Add Flutter Auth UI[#](#add-flutter-auth-ui)

Add the latest version of the package [supabase-auth-ui](https://pub.dev/packages/supabase_auth_ui) to pubspec.yaml:

```
1flutter pub add supabase_auth_ui
```

### Initialize the Flutter Auth package[#](#initialize-the-flutter-auth-package)

```
1234567891011import 'package:flutter/material.dart';import 'package:supabase_auth_ui/supabase_auth_ui.dart';void main() async {  await Supabase.initialize(    url: dotenv.get('SUPABASE_URL'),    anonKey: dotenv.get('SUPABASE_ANON_KEY'),  );  runApp(const MyApp());}
```

### Email Auth[#](#email-auth)

Use a `SupaEmailAuth` widget to create an email and password signin and signup form. It also contains a button to toggle to display a forgot password form.

You can pass `metadataFields` to add additional fields to the form to pass as metadata to Supabase.

```
123456789101112131415161718SupaEmailAuth(  redirectTo: kIsWeb ? null : 'io.mydomain.myapp://callback',  onSignInComplete: (response) {},  onSignUpComplete: (response) {},  metadataFields: [    MetaDataField(    prefixIcon: const Icon(Icons.person),    label: 'Username',    key: 'username',    validator: (val) {            if (val == null || val.isEmpty) {            return 'Please enter something';            }            return null;          },        ),    ],)
```

### Magic link Auth[#](#magic-link-auth)

Use `SupaMagicAuth` widget to create a magic link signIn form.

```
12345SupaMagicAuth(  redirectUrl: kIsWeb ? null : 'io.mydomain.myapp://callback',  onSuccess: (Session response) {},  onError: (error) {},)
```

### Reset password[#](#reset-password)

Use `SupaResetPassword` to create a password reset form.

```
12345SupaResetPassword(  accessToken: supabase.auth.currentSession?.accessToken,  onSuccess: (UserResponse response) {},  onError: (error) {},)
```

### Phone Auth[#](#phone-auth)

Use `SupaPhoneAuth` to create a phone authentication form.

```
1234SupaPhoneAuth(  authAction: SupaAuthAction.signUp,  onSuccess: (AuthResponse response) {},),
```

### Social Auth[#](#social-auth)

The package supports login with [official social providers](https://supabase.com/docs/guides/auth#providers).

Use `SupaSocialsAuth` to create list of social login buttons.

```
123456789101112SupaSocialsAuth(  socialProviders: [    OAuthProvider.apple,    OAuthProvider.google,  ],  colored: true,  redirectUrl: kIsWeb    ? null    : 'io.mydomain.myapp://callback',  onSuccess: (Session response) {},  onError: (error) {},)
```

### Theming[#](#theming)

This package uses plain Flutter components allowing you to control the appearance of the components using your own theme.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/auth-helpers/flutter-auth-ui.mdx)

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