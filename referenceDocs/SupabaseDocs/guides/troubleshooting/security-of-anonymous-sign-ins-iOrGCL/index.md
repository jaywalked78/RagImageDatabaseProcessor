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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Security of Anonymous Sign-ins

Last edited: 2/21/2025

* * *

We want to clarify and provide reassurance on this topic.

### Security overview:[#](#security-overview)

Enabling anonymous sign-ins on your project does not reduce its security. Here's why:

-   Same as Regular Users: Anonymous users function just like regular users within your project. They have unique user IDs and their own records in the authentication tables.
-   Security Policies: All role-based security policies (RLS) applicable to regular users also apply to anonymous users.
-   Identity Verification Measures: Even though anonymous users do not initially provide an email or phone number, the security of your project remains robust. But to prevent misuse, we recommend implementing additional security measure such as [CAPTCHA](https://supabase.com/docs/guides/auth/auth-captcha): to ensure that interactions are genuinely human.

### Practical use cases:[#](#practical-use-cases)

-   Demo Mode: You can enable users to try out your product in a demo mode without full account creation.
-   Feature Restrictions: You can limit certain actions (like posting public content) to users who sign up with more identifiable information (e.g., Google or Apple sign-ins), while still allowing anonymous users to explore your app.

Remember, the underlying security of your project will remain the same. If your project was secure before enabling anonymous sign-ins, it will continue to be secure afterwards. It's important to review and adjust your RLS policies regularly to align with your security and business needs.

If you have further questions or need assistance in setting up, don't hesitate to contact the [support team](https://supabase.com/dashboard/support/new).

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[anonymous](https://supabase.com/docs/guides/troubleshooting?tags=anonymous)[security](https://supabase.com/docs/guides/troubleshooting?tags=security)[sign-in](https://supabase.com/docs/guides/troubleshooting?tags=sign-in)[authentication](https://supabase.com/docs/guides/troubleshooting?tags=authentication)[identity](https://supabase.com/docs/guides/troubleshooting?tags=identity)[policies](https://supabase.com/docs/guides/troubleshooting?tags=policies)

* * *

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