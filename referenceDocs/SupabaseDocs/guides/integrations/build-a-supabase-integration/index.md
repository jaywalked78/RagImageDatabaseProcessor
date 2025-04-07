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

3.  Build Your Own

5.  [Build a Supabase integration](https://supabase.com/docs/guides/integrations/build-a-supabase-integration)

# 

Build a Supabase Integration (Beta)

## 

This guide steps through building a Supabase Integration using OAuth2 and the management API, allowing you to manage users' organizations and projects on their behalf.

* * *

Using OAuth2.0 you can retrieve an access and refresh token that grant your application full access to the [Management API](https://supabase.com/docs/reference/api/introduction) on behalf of the user.

## Create an OAuth app[#](#create-an-oauth-app)

1.  In your organization's settings, navigate to the [**OAuth Apps**](https://supabase.com/dashboard/org/_/apps) tab.
2.  In the upper-right section of the page, click **Add application**.
3.  Fill in the required details and click **Confirm**.

## Show a "Connect Supabase" button[#](#show-a-connect-supabase-button)

In your user interface, add a "Connect Supabase" button to kick off the OAuth flow. Follow the design guidelines outlined in our [brand assets](https://supabase.com/brand-assets).

## Implementing the OAuth 2.0 flow[#](#implementing-the-oauth-20-flow)

Once you've published your OAuth App on Supabase, you can use the OAuth 2.0 protocol get authorization from Supabase users to manage their organizations and projects.

You can use your preferred OAuth2 client or follow the steps below. You can see an example implementation in TypeScript using Supabase Edge Functions [on our GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/connect-supabase).

### Redirecting to the authorize URL[#](#redirecting-to-the-authorize-url)

Within your app's UI, redirect the user to [`https://api.supabase.com/v1/oauth/authorize`](https://api.supabase.com/api/v1#/oauth%20\(beta\)/authorize). Make sure to include all required query parameters such as:

-   `client_id`: Your client id from the app creation above.
-   `redirect_uri`: The URL where Supabase will redirect the user to after providing consent.
-   `response_type`: Set this to `code`.
-   `state`: Information about the state of your app. Note that `redirect_uri` and `state` together cannot exceed 4kB in size.
-   (Recommended) PKCE: We strongly recommend using the PKCE flow for increased security. Generate a random value before taking the user to the authorize endpoint. This value is called code verifier. Hash it with SHA256 and include it as the `code_challenge` parameter, while setting `code_challenge_method` to `S256`. In the next step, you would need to provide the code verifier to get the first access and refresh token.
-   \[deprecated\] `scope`: Scopes are configured when you create your OAuth app. Read the [docs](https://supabase.com/docs/guides/platform/oauth-apps/oauth-scopes) for more details.

```
123456789101112router.get('/connect-supabase/login', async (ctx) => {  // Construct the URL for the authorization redirect and get a PKCE codeVerifier.  const { uri, codeVerifier } = await oauth2Client.code.getAuthorizationUri()  console.log(uri.toString())  // console.log: https://api.supabase.com/v1/oauth/authorize?response_type=code&client_id=7673bde9-be72-4d75-bd5e-b0dba2c49b38&redirect_uri=http%3A%2F%2Flocalhost%3A54321%2Ffunctions%2Fv1%2Fconnect-supabase%2Foauth2%2Fcallback&scope=all&code_challenge=jk06R69S1bH9dD4td8mS5kAEFmEbMP5P0YrmGNAUVE0&code_challenge_method=S256  // Store the codeVerifier in the user session (cookie).  ctx.state.session.flash('codeVerifier', codeVerifier)  // Redirect the user to the authorization endpoint.  ctx.response.redirect(uri)})
```

Find the full example on [GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/connect-supabase).

### Handling the callback[#](#handling-the-callback)

Once the user consents to providing API access to your OAuth App, Supabase will redirect the user to the `redirect_uri` provided in the previous step. The URL will contain these query parameters:

-   `code`: An authorization code you should exchange with Supabase to get the access and refresh token.
-   `state`: The value you provided in the previous step, to help you associate the request with the user. The `state` property returned here should be compared to the `state` you sent previously.

Exchange the authorization code for an access and refresh token by calling [`POST https://api.supabase.com/v1/oauth/token`](https://api.supabase.com/api/v1#/oauth%20\(beta\)/token) with the following query parameters as content-type `application/x-www-form-urlencoded`:

-   `grant_type`: The value `authorization_code`.
-   `code`: The `code` returned in the previous step.
-   `redirect_uri`: This must be exactly the same URL used in the first step.
-   (Recommended) `code_verifier`: If you used the PKCE flow in the first step, include the code verifier as `code_verifier`.

If your application need to support dynamically generated Redirect URLs, check out [Handling Dynamic Redirect URLs](#handling-dynamic-redirect-urls) section below.

As per OAuth2 spec, provide the client id and client secret as basic auth header:

-   `client_id`: The unique client ID identifying your OAuth App.
-   `client_secret`: The secret that authenticates your OAuth App to Supabase.

```
1234567891011121314151617181920212223242526router.get('/connect-supabase/oauth2/callback', async (ctx) => {  // Make sure the codeVerifier is present for the user's session.  const codeVerifier = ctx.state.session.get('codeVerifier') as string  if (!codeVerifier) throw new Error('No codeVerifier!')  // Exchange the authorization code for an access token.  const tokens = await fetch(config.tokenUri, {    method: 'POST',    headers: {      'Content-Type': 'application/x-www-form-urlencoded',      Accept: 'application/json',      Authorization: `Basic ${btoa(`${config.clientId}:${config.clientSecret}`)}`,    },    body: new URLSearchParams({      grant_type: 'authorization_code',      code: ctx.request.url.searchParams.get('code') || '',      redirect_uri: config.redirectUri,      code_verifier: codeVerifier,    }),  }).then((res) => res.json())  console.log('tokens', tokens)  // Store the tokens in your DB for future use.  ctx.response.body = 'Success'})
```

Find the full example on [GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/connect-supabase).

## Refreshing an access token[#](#refreshing-an-access-token)

You can use the [`POST /v1/oauth/token`](https://api.supabase.com/api/v1#/oauth%20\(beta\)/token) endpoint to refresh an access token using the refresh token returned at the end of the previous section.

If the user has revoked access to your application, you will not be able to refresh a token. Furthermore, access tokens will stop working. Make sure you handle HTTP Unauthorized errors when calling any Supabase API.

## Calling the Management API[#](#calling-the-management-api)

Refer to [the Management API reference](https://supabase.com/docs/reference/api/introduction#authentication) to learn more about authentication with the Management API.

### Use the JavaScript (TypeScript) SDK[#](#use-the-javascript-typescript-sdk)

For convenience, when working with JavaScript/TypeScript, you can use the [supabase-management-js](https://github.com/supabase-community/supabase-management-js#supabase-management-js) library.

```
123import { SupabaseManagementAPI } from 'supabase-management-js'const client = new SupabaseManagementAPI({ accessToken: '<access token>' })
```

## Integration recommendations[#](#integration-recommendations)

There are a couple common patterns you can consider adding to your integration that can facilitate a great user experience.

### Store API keys in env variables[#](#store-api-keys-in-env-variables)

Some integrations, e.g. like [Cloudflare Workers](https://supabase.com/partners/integrations/cloudflare-workers) provide convenient access to the API URL and API keys to allow user to speed up development.

Using the management API, you can retrieve a project's API credentials using the [`/projects/{ref}/api-keys` endpoint](https://api.supabase.com/api/v1#/projects/getProjectApiKeys).

### Pre-fill database connection details[#](#pre-fill-database-connection-details)

If your integration directly connects to the project's database, you can pref-fill the Postgres connection details for the user, it follows this schema:

```
1postgresql://postgres:[DB-PASSWORD]@db.[REF].supabase.co:5432/postgres
```

Note that you cannot retrieve the database password via the management API, so for the user's existing projects you will need to collect their database password in your UI.

### Create new projects[#](#create-new-projects)

Use the [`/v1/projects` endpoint](https://api.supabase.com/api/v1#/projects/createProject) to create a new project.

When creating a new project, you can either ask the user to provide a database password, or you can generate a secure password for them. In any case, make sure to securely store the database password on your end which will allow you to construct the Postgres URI.

### Configure custom Auth SMTP[#](#configure-custom-auth-smtp)

You can configure the user's [custom SMTP settings](https://supabase.com/docs/guides/auth/auth-smtp) using the [`/config/auth` endpoint](https://api.supabase.com/api/v1#/projects%20config/updateV1AuthConfig).

### Handling dynamic redirect URLs[#](#handling-dynamic-redirect-urls)

To handle multiple, dynamically generated redirect URLs within the same OAuth app, you can leverage the `state` query parameter. When starting the OAuth process, include the desired, encoded redirect URL in the `state` parameter. Once authorization is complete, we will sends the `state` value back to your app. You can then verify its integrity and extract the correct redirect URL, decoding it and redirecting the user to the correct URL.

## Current limitations[#](#current-limitations)

Only some features are available until we roll out fine-grained access control. If you need full database access, you will need to prompt the user for their database password.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/integrations/build-a-supabase-integration.mdx)

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