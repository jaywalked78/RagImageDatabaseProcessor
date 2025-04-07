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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  Platform Configuration

5.  [HIPAA Projects](https://supabase.com/docs/guides/platform/hipaa-projects)

# 

HIPAA Projects

* * *

You can use Supabase to store and process Protected Health Information (PHI). If you want to start developing healthcare apps on Supabase, reach out to the Supabase team [here](https://forms.supabase.com/hipaa2) to sign the Business Associate Agreement (BAA).

Organizations must have a signed BAA with Supabase and have the Health Insurance Portability and Accountability Act (HIPAA) add-on enabled when dealing with PHI.

## Configuring a HIPAA project[#](#configuring-a-hipaa-project)

When the HIPAA add-on is enabled on an organization, projects within the organization can be configured as _High Compliance_. This configuration can be found in the [General Project Settings page](https://supabase.com/dashboard/project/_/settings) of the dashboard. Once enabled, additional security checks will be run against the project to ensure the deployed configuration is compliant. These checks are performed on a continual basis and security warnings will appear in the [Security Advisor](https://supabase.com/dashboard/project/_/advisors/security) if a non-compliant setting is detected.

The required project configuration is outlined in the [shared responsibility model](https://supabase.com/docs/guides/deployment/shared-responsibility-model#managing-healthcare-data) for managing healthcare data.

These include:

-   Enabling [Point in Time Recovery](https://supabase.com/docs/guides/platform/backups#point-in-time-recovery) which requires at least a [small compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons).
-   Turning on [SSL Enforcement](https://supabase.com/docs/guides/platform/ssl-enforcement).
-   Enabling [Network Restrictions](https://supabase.com/docs/guides/platform/network-restrictions).

Additional security checks and controls will be added as the security advisor is extended and additional security controls are made available.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/hipaa-projects.mdx)

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