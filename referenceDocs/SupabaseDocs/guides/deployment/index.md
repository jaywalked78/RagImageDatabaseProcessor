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

Home

1.  [Deployment](https://supabase.com/docs/guides/deployment)

3.  [Overview](https://supabase.com/docs/guides/deployment)

# 

Deployment

* * *

Deploying your app makes it live and accessible to users. Usually, you will deploy an app to at least two environments: a production environment for users and (one or multiple) staging or preview environments for developers.

Supabase provides several options for environment management and deployment.

## Environment management[#](#environment-management)

You can maintain separate development, staging, and production environments for Supabase:

-   **Development**: Develop with a local Supabase stack using the [Supabase CLI](https://supabase.com/docs/guides/local-development).
-   **Staging**: Use [branching](https://supabase.com/docs/guides/deployment/branching) to create staging or preview environments. You can use persistent branches for a long-lived staging setup, or ephemeral branches for short-lived previews (which are often tied to a pull request).
-   **Production**: If you have branching enabled, you can use the Supabase GitHub integration to automatically push your migration files when you merge a pull request. Alternatively, you can set up your own continuous deployment pipeline using the Supabase CLI.

##### Self-hosting

See the [self-hosting guides](https://supabase.com/docs/guides/self-hosting) for instructions on hosting your own Supabase stack.

## Deployment[#](#deployment)

You can automate deployments using:

-   The [Supabase GitHub integration](https://supabase.com/dashboard/project/_/settings/integrations) (with branching enabled)
-   The [Supabase CLI](https://supabase.com/docs/guides/local-development) in your own continuous deployment pipeline
-   The [Supabase Terraform provider](https://supabase.com/docs/guides/deployment/terraform)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/deployment.mdx)

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