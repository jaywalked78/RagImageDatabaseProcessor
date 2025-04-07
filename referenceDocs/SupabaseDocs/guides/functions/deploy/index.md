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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Getting started

5.  [Deploy to Production](https://supabase.com/docs/guides/functions/deploy)

# 

Deploy to Production

## 

Deploy your Edge Functions to your remote Supabase Project.

* * *

Once you have developed your Edge Functions locally, you can deploy them to your Supabase project.

## Login to the CLI[#](#login-to-the-cli)

Log in to the Supabase CLI if necessary:

```
1supabase login
```

##### CLI not installed?

See the [CLI Docs](https://supabase.com/docs/guides/cli) to learn how to install the Supabase CLI on your local machine.

## Get your project ID[#](#get-your-project-id)

Get the project ID associated with your function by running:

```
1supabase projects list
```

##### Need a new project?

If you haven't yet created a Supabase project, you can do so by visiting [database.new](https://database.new).

## Link your local project[#](#link-your-local-project)

[Link](https://supabase.com/docs/reference/cli/usage#supabase-link) your local project to your remote Supabase project using the ID you just retrieved:

```
1supabase link --project-ref your-project-id
```

## Deploy your Edge Functions[#](#deploy-your-edge-functions)

##### Docker required

Since Supabase CLI version 1.123.4, you must have [Docker Desktop](https://docs.docker.com/desktop/) installed to deploy Edge Functions.

You can deploy all of your Edge Functions with a single command:

```
1supabase functions deploy
```

You can deploy individual Edge Functions by specifying the name of the function in the deploy command:

```
1supabase functions deploy hello-world
```

By default, Edge Functions require a valid JWT in the authorization header. If you want to use Edge Functions without Authorization checks (commonly used for Stripe webhooks), you can pass the `--no-verify-jwt` flag when deploying your Edge Functions.

```
1supabase functions deploy hello-world --no-verify-jwt
```

Be careful when using this flag, as it will allow anyone to invoke your Edge Function without a valid JWT. The Supabase client libraries automatically handle authorization.

## Invoking remote functions[#](#invoking-remote-functions)

You can now invoke your Edge Function using the project's `ANON_KEY`, which can be found in the [API settings](https://supabase.com/dashboard/project/_/settings/api) of the Supabase Dashboard.

cURLJavaScript

```
1234curl --request POST 'https://<project_id>.supabase.co/functions/v1/hello-world' \  --header 'Authorization: Bearer ANON_KEY' \  --header 'Content-Type: application/json' \  --data '{ "name":"Functions" }'
```

You should receive the response `{ "message":"Hello Functions!" }`.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/deploy.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F5OWH9c4u68M%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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