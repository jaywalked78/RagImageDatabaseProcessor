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

# Rotating Anon, Service, and JWT Secrets

Last edited: 2/21/2025

* * *

Have you ever accidentally committed a service key to a public repo? Or maybe rotating keys is just something you regularly do for security compliance. Whatever the reason, here's how to rotate the keys for your Supabase project.

1.  Go to the [API Settings page](https://supabase.com/dashboard/project/_/settings/api) in the Supabase Dashboard
2.  Find the JWT Secrets section

![Screenshot 2023-12-27 at 08 39 41](https://github.com/supabase/supabase/assets/1923424/bdcab8a2-7007-496c-a845-d331ee883a0a)

3.  Click the `Generate new secret` button and choose either a random secret, or custom if you'd like to supply one of your own.
4.  NOTE: Once regenerated, all current API secrets will be immediately invalidated, and all connections using them will be severed. You will need to deploy the new secrets for connections to begin working again.
5.  Confirm the changes in the warning that pops up by clicking `Generate New Secret` again.

![Screenshot 2023-12-27 at 08 39 59](https://github.com/supabase/supabase/assets/1923424/1f5cf876-ff65-41f0-b92e-37826773041c)

6.  After confirming, the secret will be generated, and Supabase will start rolling that out across our services. Postgres will restart, the API gateways will be updated, etc. Once the process is complete, you will be able to see your new JWT secret as well as the new anon and service keys.

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[jwt](https://supabase.com/docs/guides/troubleshooting?tags=jwt)[secrets](https://supabase.com/docs/guides/troubleshooting?tags=secrets)[key](https://supabase.com/docs/guides/troubleshooting?tags=key)[security](https://supabase.com/docs/guides/troubleshooting?tags=security)

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