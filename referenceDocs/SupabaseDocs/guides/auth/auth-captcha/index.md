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

3.  Security

5.  [Bot Detection (CAPTCHA)](https://supabase.com/docs/guides/auth/auth-captcha)

# 

Enable CAPTCHA Protection

* * *

Supabase provides you with the option of adding CAPTCHA to your sign-in, sign-up, and password reset forms. This keeps your website safe from bots and malicious scripts. Supabase authentication has support for [hCaptcha](https://www.hcaptcha.com/) and [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/).

## Sign up for CAPTCHA[#](#sign-up-for-captcha)

HCaptchaTurnstile

Go to the [hCaptcha](https://www.hcaptcha.com/) website and sign up for an account. On the Welcome page, copy the **Sitekey** and **Secret key**.

If you have already signed up and didn't copy this information from the Welcome page, you can get the **Secret key** from the Settings page.

![site_secret_settings.png](https://supabase.com/docs/img/guides/auth-captcha/site_secret_settings.png)

The **Sitekey** can be found in the **Settings** of the active site you created.

![sites_dashboard.png](https://supabase.com/docs/img/guides/auth-captcha/sites_dashboard.png)

In the Settings page, look for the **Sitekey** section and copy the key.

![sitekey_settings.png](https://supabase.com/docs/img/guides/auth-captcha/sitekey_settings.png)

## Enable CAPTCHA protection for your Supabase project[#](#enable-captcha-protection-for-your-supabase-project)

Navigate to the **[Auth](https://supabase.com/dashboard/project/_/settings/auth)** section of your Project Settings in the Supabase Dashboard and find the **Enable CAPTCHA protection** toggle under Settings > Authentication > Bot and Abuse Protection > Enable CAPTCHA protection.

Select your CAPTCHA provider from the dropdown, enter your CAPTCHA **Secret key**, and click **Save**.

## Add the CAPTCHA frontend component[#](#add-the-captcha-frontend-component)

The frontend requires some changes to provide the CAPTCHA on-screen for the user. This example uses React and the corresponding CAPTCHA React component, but both CAPTCHA providers can be used with any JavaScript framework.

HCaptchaTurnstile

Install `@hcaptcha/react-hcaptcha` in your project as a dependency.

```
1npm install @hcaptcha/react-hcaptcha
```

Now import the `HCaptcha` component from the `@hcaptcha/react-hcaptcha` library.

```
1import HCaptcha from '@hcaptcha/react-hcaptcha'
```

Let's create a empty state to store our `captchaToken`

```
1const [captchaToken, setCaptchaToken] = useState()
```

Now lets add the `HCaptcha` component to the JSX section of our code

```
1<HCaptcha />
```

We will pass it the sitekey we copied from the hCaptcha website as a property along with a `onVerify` property which takes a callback function. This callback function will have a token as one of its properties. Let's set the token in the state using `setCaptchaToken`

```
123456<HCaptcha  sitekey="your-sitekey"  onVerify={(token) => {    setCaptchaToken(token)  }}/>
```

Now lets use the CAPTCHA token we receive in our Supabase signUp function.

```
12345await supabase.auth.signUp({  email,  password,  options: { captchaToken },})
```

We will also need to reset the CAPTCHA challenge after we have made a call to the function above.

Create a ref to use on our `HCaptcha` component.

```
1const captcha = useRef()
```

Let's add a ref attribute on the `HCaptcha` component and assign the `captcha` constant to it.

```
1234567<HCaptcha  ref={captcha}  sitekey="your-sitekey"  onVerify={(token) => {    setCaptchaToken(token)  }}/>
```

Reset the `captcha` after the signUp function is called using the following code:

```
1captcha.current.resetCaptcha()
```

In order to test that this works locally we will need to use something like [ngrok](https://ngrok.com/) or add an entry to your hosts file. You can read more about this in the [hCaptcha docs](https://docs.hcaptcha.com/#local-development).

Run the application and you should now be provided with a CAPTCHA challenge.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/auth-captcha.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2Fem1cpOAXknM%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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