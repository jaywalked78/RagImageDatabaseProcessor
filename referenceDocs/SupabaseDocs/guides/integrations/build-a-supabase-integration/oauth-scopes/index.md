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

Integrations

1.  [Integrations](https://supabase.com/docs/guides/integrations)

3.  More

5.  [Build a Supabase integration](https://supabase.com/docs/guides/integrations/build-a-supabase-integration)

7.  [OAuth scopes](https://supabase.com/docs/guides/integrations/build-a-supabase-integration/oauth-scopes)

# 

Scopes for your OAuth App

## 

Scopes let you specify the level of access your integration needs

* * *

Scopes are only available for OAuth apps. Check out [**our guide**](https://supabase.com/docs/guides/platform/oauth-apps/build-a-supabase-integration) to learn how to build an OAuth app integration.

Scopes restrict access to the specific [Supabase Management API endpoints](https://supabase.com/docs/reference/api/introduction) for OAuth tokens. All scopes can be specified as read and/or write.

Scopes are set when you [create an OAuth app](https://supabase.com/docs/guides/platform/oauth-apps/build-a-supabase-integration#create-an-oauth-app) in the Supabase Dashboard.

## Available scopes[#](#available-scopes)

| Name | Type | Description |
| --- | --- | --- |
| `Auth` | `Read` | Retrieve a project's auth configuration  
Retrieve a project's SAML SSO providers |
| `Auth` | `Write` | Update a project's auth configuration  
Create, update, or delete a project's SAML SSO providers |
| `Database` | `Read` | Retrieve the database configuration  
Retrieve the pooler configuration  
Retrieve SQL snippets  
Check if the database is in read-only mode  
Retrieve a database's SSL enforcement configuration  
Retrieve a database's schema typescript types |
| `Database` | `Write` | Create a SQL query  
Enable database webhooks on the project  
Update the project's database configuration  
Update the pooler configuration  
Update a database's SSL enforcement configuration  
Disable read-only mode for 15mins  
Create a PITR backup for a database |
| `Domains` | `Read` | Retrieve the custom domains for a project  
Retrieve the vanity subdomain configuration for a project |
| `Domains` | `Write` | Activate, initialize, reverify, or delete the custom domain for a project  
Activate, delete or check the availability of a vanity subdomain for a project |
| `Edge Functions` | `Read` | Retrieve information about a project's edge functions |
| `Edge Functions` | `Write` | Create, update, or delete an edge function |
| `Environment` | `Read` | Retrieve branches in a project |
| `Environment` | `Write` | Create, update, or delete a branch |
| `Organizations` | `Read` | Retrieve an organization's metadata  
Retrieve all members in an organization |
| `Organizations` | `Write` | N/A |
| `Projects` | `Read` | Retrieve a project's metadata  
Check if a project's database is eligible for upgrade  
Retrieve a project's network restrictions  
Retrieve a project's network bans |
| `Projects` | `Write` | Create a project  
Upgrade a project's database  
Remove a project's network bans  
Update a project's network restrictions |
| `Rest` | `Read` | Retrieve a project's PostgREST configuration |
| `Rest` | `Write` | Update a project's PostgREST configuration |
| `Secrets` | `Read` | Retrieve a project's API keys  
Retrieve a project's secrets  
Retrieve a project's pgsodium config |
| `Secrets` | `Write` | Create or update a project's secrets  
Update a project's pgsodium configuration |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/integrations/build-a-supabase-integration/oauth-scopes.mdx)

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