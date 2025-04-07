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

Getting Started

1.  [Start with Supabase](https://supabase.com/docs/guides/getting-started)

3.  [Features](https://supabase.com/docs/guides/getting-started/features)

# 

Features

* * *

This is a non-exhaustive list of features that Supabase provides for every project.

## Database[#](#database)

### Postgres database[#](#postgres-database)

Every project is a full Postgres database. [Docs](https://supabase.com/docs/guides/database).

### Vector database[#](#vector-database)

Store vector embeddings right next to the rest of your data. [Docs](https://supabase.com/docs/guides/ai).

### Auto-generated REST API via PostgREST[#](#auto-generated-rest-api-via-postgrest)

RESTful APIs are auto-generated from your database, without a single line of code. [Docs](https://supabase.com/docs/guides/api#rest-api-overview).

### Auto-generated GraphQL API via pg\_graphql[#](#auto-generated-graphql-api-via-pggraphql)

Fast GraphQL APIs using our custom Postgres GraphQL extension. [Docs](https://supabase.com/docs/guides/graphql/api).

### Database webhooks[#](#database-webhooks)

Send database changes to any external service using Webhooks. [Docs](https://supabase.com/docs/guides/database/webhooks).

### Secrets and encryption[#](#secrets-and-encryption)

Encrypt sensitive data and store secrets using our Postgres extension, Supabase Vault. [Docs](https://supabase.com/docs/guides/database/vault).

## Platform[#](#platform)

### Database backups[#](#database-backups)

Projects are backed up daily with the option to upgrade to Point in Time recovery. [Docs](https://supabase.com/docs/guides/platform/backups).

### Custom domains[#](#custom-domains)

White-label the Supabase APIs to create a branded experience for your users. [Docs](https://supabase.com/docs/guides/platform/custom-domains).

### Network restrictions[#](#network-restrictions)

Restrict IP ranges that can connect to your database. [Docs](https://supabase.com/docs/guides/platform/network-restrictions).

### SSL enforcement[#](#ssl-enforcement)

Enforce Postgres clients to connect via SSL. [Docs](https://supabase.com/docs/guides/platform/ssl-enforcement).

### Branching[#](#branching)

Use Supabase Branches to test and preview changes. [Docs](https://supabase.com/docs/guides/platform/branching).

### Terraform provider[#](#terraform-provider)

Manage Supabase infrastructure via Terraform, an Infrastructure as Code tool. [Docs](https://supabase.com/docs/guides/platform/terraform).

### Read replicas[#](#read-replicas)

Deploy read-only databases across multiple regions, for lower latency and better resource management. [Docs](https://supabase.com/docs/guides/platform/read-replicas).

### Log drains[#](#log-drains)

Export Supabase logs at to 3rd party providers and external tooling. [Docs](https://supabase.com/docs/guides/platform/log-drains).

## Studio[#](#studio)

### Studio Single Sign-On[#](#studio-single-sign-on)

Login to the Supabase dashboard via SSO. [Docs](https://supabase.com/docs/guides/platform/sso).

  

## Realtime[#](#realtime)

### Postgres changes[#](#postgres-changes)

Receive your database changes through WebSockets. [Docs](https://supabase.com/docs/guides/realtime/postgres-changes).

### Broadcast[#](#broadcast)

Send messages between connected users through WebSockets. [Docs](https://supabase.com/docs/guides/realtime/broadcast).

### Presence[#](#presence)

Synchronize shared state across your users, including online status and typing indicators. [Docs](https://supabase.com/docs/guides/realtime/presence).

## Auth[#](#auth)

### Email login[#](#email-login)

Build email logins for your application or website. [Docs](https://supabase.com/docs/guides/auth/auth-email).

### Social login[#](#social-login)

Provide social logins - everything from Apple, to GitHub, to Slack. [Docs](https://supabase.com/docs/guides/auth/social-login).

### Phone logins[#](#phone-logins)

Provide phone logins using a third-party SMS provider. [Docs](https://supabase.com/docs/guides/auth/phone-login).

### Passwordless login[#](#passwordless-login)

Build passwordless logins via magic links for your application or website. [Docs](https://supabase.com/docs/guides/auth/auth-magic-link).

### Authorization via Row Level Security[#](#authorization-via-row-level-security)

Control the data each user can access with Postgres Policies. [Docs](https://supabase.com/docs/guides/database/postgres/row-level-security).

### CAPTCHA protection[#](#captcha-protection)

Add CAPTCHA to your sign-in, sign-up, and password reset forms. [Docs](https://supabase.com/docs/guides/auth/auth-captcha).

### Server-Side Auth[#](#server-side-auth)

Helpers for implementing user authentication in popular server-side languages and frameworks like Next.js, SvelteKit and Remix. [Docs](https://supabase.com/docs/guides/auth/server-side).

  

## Storage[#](#storage)

### File storage[#](#file-storage)

Supabase Storage makes it simple to store and serve files. [Docs](https://supabase.com/docs/guides/storage).

### Content Delivery Network[#](#content-delivery-network)

Cache large files using the Supabase CDN. [Docs](https://supabase.com/docs/guides/storage/cdn/fundamentals).

### Smart Content Delivery Network[#](#smart-content-delivery-network)

Automatically revalidate assets at the edge via the Smart CDN. [Docs](https://supabase.com/docs/guides/storage/cdn/smart-cdn).

### Image transformations[#](#image-transformations)

Transform images on the fly. [Docs](https://supabase.com/docs/guides/storage/serving/image-transformations).

### Resumable uploads[#](#resumable-uploads)

Upload large files using resumable uploads. [Docs](https://supabase.com/docs/guides/storage/uploads/resumable-uploads).

### S3 compatibility[#](#s3-compatibility)

Interact with Storage from tool which supports the S3 protocol. [Docs](https://supabase.com/docs/guides/storage/s3/compatibility).

## Edge Functions[#](#edge-functions)

### Deno Edge Functions[#](#deno-edge-functions)

Globally distributed TypeScript functions to execute custom business logic. [Docs](https://supabase.com/docs/guides/functions).

### Regional invocations[#](#regional-invocations)

Execute an Edge Function in a region close to your database. [Docs](https://supabase.com/docs/guides/functions/regional-invocation).

### NPM compatibility[#](#npm-compatibility)

Edge functions natively support NPM modules and Node built-in APIs. [Link](https://supabase.com/blog/edge-functions-node-npm).

## Project management[#](#project-management)

### CLI[#](#cli)

Use our CLI to develop your project locally and deploy to the Supabase Platform. [Docs](https://supabase.com/docs/reference/cli).

### Management API[#](#management-api)

Manage your projects programmatically. [Docs](https://supabase.com/docs/reference/api).

## Client libraries[#](#client-libraries)

Official client libraries for [JavaScript](https://supabase.com/docs/reference/javascript/start), [Flutter](https://supabase.com/docs/reference/dart/initializing) and [Swift](https://supabase.com/docs/reference/swift/introduction). Unofficial libraries are supported by the community.

## Feature status[#](#feature-status)

Supabase Features are in 4 different states - Private Alpha, Public Alpha, Beta and Generally Available.

### Private alpha[#](#private-alpha)

Features are initially launched as a private alpha to gather feedback from the community. To join our early access program, send an email to [product-ops@supabase.io](mailto:product-ops@supabase.io).

### Public alpha[#](#public-alpha)

The alpha stage indicates that the API might change in the future, not that the service isn’t stable. Even though the [uptime Service Level Agreement](https://supabase.com/sla) does not cover products in Alpha, we do our best to have the service as stable as possible.

### Beta[#](#beta)

Features in Beta are tested by an external penetration tester for security issues. The API is guaranteed to be stable and there is a strict communication process for breaking changes.

### Generally available[#](#generally-available)

In addition to the Beta requirements, features in GA are covered by the [uptime SLA](https://supabase.com/sla).

| Product | Feature | Stage | Available on self-hosted |
| --- | --- | --- | --- |
| Database | Postgres | `GA` | ✅ |
| Database | Vector Database | `GA` | ✅ |
| Database | Auto-generated Rest API | `GA` | ✅ |
| Database | Auto-generated GraphQL API | `GA` | ✅ |
| Database | Webhooks | `beta` | ✅ |
| Database | Vault | `public alpha` | ✅ |
| Platform |  | `GA` | ✅ |
| Platform | Point-in-Time Recovery | `GA` | 🚧 [wal-g](https://github.com/wal-g/wal-g) |
| Platform | Custom Domains | `GA` | N/A |
| Platform | Network Restrictions | `beta` | N/A |
| Platform | SSL enforcement | `GA` | N/A |
| Platform | Branching | `public alpha` | N/A |
| Platform | Terraform Provider | `public alpha` | N/A |
| Platform | Read Replicas | `private alpha` | N/A |
| Platform | Log Drains | `public alpha` | ✅ |
| Studio |  | `GA` | ✅ |
| Studio | SSO | `GA` | ✅ |
| Realtime | Postgres Changes | `GA` | ✅ |
| Realtime | Broadcast | `GA` | ✅ |
| Realtime | Presence | `GA` | ✅ |
| Realtime | Broadcast Authorization | `public beta` | ✅ |
| Realtime | Presence Authorization | `public beta` | ✅ |
| Storage |  | `GA` | ✅ |
| Storage | CDN | `GA` | 🚧 [Cloudflare](https://www.cloudflare.com) |
| Storage | Smart CDN | `GA` | 🚧 [Cloudflare](https://www.cloudflare.com) |
| Storage | Image Transformations | `GA` | ✅ |
| Storage | Resumable Uploads | `GA` | ✅ |
| Storage | S3 compatibility | `public alpha` | ✅ |
| Edge Functions |  | `beta` | ✅ |
| Edge Functions | Regional Invocations | `beta` | ✅ |
| Edge Functions | NPM compatibility | `beta` | ✅ |
| Auth |  | `GA` | ✅ |
| Auth | Email login | `GA` | ✅ |
| Auth | Social login | `GA` | ✅ |
| Auth | Phone login | `GA` | ✅ |
| Auth | Passwordless login | `GA` | ✅ |
| Auth | SSO with SAML | `GA` | ✅ |
| Auth | Authorization via RLS | `GA` | ✅ |
| Auth | CAPTCHA protection | `GA` | ✅ |
| Auth | Server-side Auth | `beta` | ✅ |
| CLI |  | `GA` | ✅ Works with self-hosted |
| Management API |  | `GA` | N/A |
| Client Library | JavaScript | `GA` | N/A |
| Client Library | Flutter | `beta` | N/A |
| Client Library | Swift | `beta` | N/A |

-   ✅ = Fully Available
-   🚧 = Available, but requires external tools or configuration

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/features.mdx)

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