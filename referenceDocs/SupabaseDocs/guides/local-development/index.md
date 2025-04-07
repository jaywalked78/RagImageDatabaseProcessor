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

Local Development

1.  [Local Dev / CLI](https://supabase.com/docs/guides/local-development)

3.  [Overview](https://supabase.com/docs/guides/local-development)

# 

Local Development & CLI

## 

Learn how to develop locally and use the Supabase CLI

* * *

Develop locally while running the Supabase stack on your machine.

## Quickstart[#](#quickstart)

1.  Install the Supabase CLI:
    
    npmyarnpnpmbrew
    
    ```
    1npm install supabase --save-dev
    ```
    
2.  In your repo, initialize the Supabase project:
    
    npmyarnpnpmbrew
    
    ```
    1npx supabase init
    ```
    
3.  Start the Supabase stack:
    
    npmyarnpnpmbrew
    
    ```
    1npx supabase start
    ```
    
4.  View your local Supabase instance at [http://localhost:54323](http://localhost:54323).
    

## Local development[#](#local-development)

Local development with Supabase allows you to work on your projects in a self-contained environment on your local machine. Working locally has several advantages:

1.  Faster development: You can make changes and see results instantly without waiting for remote deployments.
2.  Offline work: You can continue development even without an internet connection.
3.  Cost-effective: Local development is free and doesn't consume your project's quota.
4.  Enhanced privacy: Sensitive data remains on your local machine during development.
5.  Easy testing: You can experiment with different configurations and features without affecting your production environment.

To get started with local development, you'll need to install the [Supabase CLI](#cli) and Docker. The Supabase CLI allows you to start and manage your local Supabase stack, while Docker is used to run the necessary services.

Once set up, you can initialize a new Supabase project, start the local stack, and begin developing your application using local Supabase services. This includes access to a local Postgres database, Auth, Storage, and other Supabase features.

## CLI[#](#cli)

The Supabase CLI is a powerful tool that enables developers to manage their Supabase projects directly from the terminal. It provides a suite of commands for various tasks, including:

-   Setting up and managing local development environments
-   Generating TypeScript types for your database schema
-   Handling database migrations
-   Managing environment variables and secrets
-   Deploying your project to the Supabase platform

With the CLI, you can streamline your development workflow, automate repetitive tasks, and maintain consistency across different environments. It's an essential tool for both local development and CI/CD pipelines.

See the [CLI Getting Started guide](https://supabase.com/docs/guides/local-development/cli/getting-started) for more information.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/local-development.mdx)

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