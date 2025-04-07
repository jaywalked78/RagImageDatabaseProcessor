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

5.  [Phone Login](https://supabase.com/docs/guides/auth/phone-login)

# 

Phone Login

* * *

Phone Login is a method of authentication that allows users to log in to a website or application without using a password. The user authenticates through a one-time password (OTP) sent via a channel (SMS or WhatsApp).

At this time, `WhatsApp` is only supported as a channel for the Twilio and Twilio Verify Providers.

Users can also log in with their phones using Native Mobile Login with the built-in identity provider. For Native Mobile Login with Android and iOS, see the [Social Login guides](https://supabase.com/docs/guides/auth/social-login).

Phone OTP login can:

-   Improve the user experience by not requiring users to create and remember a password
-   Increase security by reducing the risk of password-related security breaches
-   Reduce support burden of dealing with password resets and other password-related flows

To keep SMS sending costs under control, make sure you adjust your project's rate limits and [configure CAPTCHA](https://supabase.com/docs/guides/auth/auth-captcha). See the [Production Checklist](https://supabase.com/docs/guides/platform/going-into-prod) to learn more.

  

Some countries have special regulations for services that send SMS messages to users, (e.g India's TRAI DLT regulations). Remember to look up and follow the regulations of countries where you operate.

## Enabling phone login[#](#enabling-phone-login)

Enable phone authentication on the [Auth Providers page](https://supabase.com/dashboard/project/_/auth/providers) for hosted Supabase projects.

For self-hosted projects or local development, use the [configuration file](https://supabase.com/docs/guides/cli/config#auth.sms.enable_signup). See the configuration variables namespaced under `auth.sms`.

You also need to set up an SMS provider. Each provider has its own configuration. Supported providers include MessageBird, Twilio, Vonage, and TextLocal (community-supported).

### Configuring SMS Providers

![MessageBird Icon](https://supabase.com/docs/img/icons/messagebird-icon.svg)

##### MessageBird

![Twilio Icon](https://supabase.com/docs/img/icons/twilio-icon.svg)

##### Twilio

![Vonage Icon](https://supabase.com/docs/img/icons/vonage-icon-light.svg)

##### Vonage

![Textlocal (Community Supported) Icon](https://supabase.com/docs/img/icons/textlocal-icon.svg)

##### Textlocal (Community Supported)

By default, a user can only request an OTP once every 60 seconds and they expire after 1 hour.

## Signing in with phone OTP[#](#signing-in-with-phone-otp)

With OTP, a user can sign in without setting a password on their account. They need to verify their phone number each time they sign in.

JavaScriptSwiftKotlinPythonHTTP

```
123const { data, error } = await supabase.auth.signInWithOtp({  phone: '+13334445555',})
```

The user receives an SMS with a 6-digit pin that you must verify within 60 seconds.

## Verifying a phone OTP[#](#verifying-a-phone-otp)

To verify the one-time password (OTP) sent to the user's phone number, call [`verifyOtp()`](https://supabase.com/docs/reference/javascript/auth-verifyotp) with the phone number and OTP:

JavaScriptSwiftKotlinPythonHTTP

You should present a form to the user so they can input the 6 digit pin, then send it along with the phone number to `verifyOtp`:

```
12345678const {  data: { session },  error,} = await supabase.auth.verifyOtp({  phone: '13334445555',  token: '123456',  type: 'sms',})
```

If successful the user will now be logged in and you should receive a valid session like:

```
123456{  "access_token": "<ACCESS_TOKEN>",  "token_type": "bearer",  "expires_in": 3600,  "refresh_token": "<REFRESH_TOKEN>"}
```

The access token can be sent in the Authorization header as a Bearer token for any CRUD operations on supabase-js. See our guide on [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) for more info on restricting access on a user basis.

## Updating a phone number[#](#updating-a-phone-number)

To update a user's phone number, the user must be logged in. Call [`updateUser()`](https://supabase.com/docs/reference/javascript/auth-updateuser) with their phone number:

JavaScriptSwiftKotlinPython

```
123const { data, error } = await supabase.auth.updateUser({  phone: '123456789',})
```

The user receives an SMS with a 6-digit pin that you must [verify](#verifying-a-phone-otp) within 60 seconds. Use the `phone_change` type when calling `verifyOTP` to update a user’s phone number.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/phone-login.mdx)

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