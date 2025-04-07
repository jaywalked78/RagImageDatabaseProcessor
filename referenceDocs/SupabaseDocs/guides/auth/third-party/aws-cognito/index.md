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

3.  Third-party auth

5.  [AWS Cognito (Amplify)](https://supabase.com/docs/guides/auth/third-party/aws-cognito)

# 

Amazon Cognito (Amplify)

## 

Use Amazon Cognito via Amplify or standalone with your Supabase project

* * *

Amazon Cognito User Pools (via AWS Amplify or on its own) can be used as a third-party authentication provider alongside Supabase Auth, or standalone, with your Supabase project.

## Getting started[#](#getting-started)

1.  First you need to add an integration to connect your Supabase project with your Amazon Cognito User Pool. You will need the pool's ID and region.
2.  Add a new Third-party Auth integration in your project's [Authentication settings](https://supabase.com/dashboard/project/_/settings/auth) or configure it in the CLI.
3.  Assign the `role: 'authenticated'` custom claim to all JWTs by using a Pre-Token Generation Trigger.
4.  Finally setup the Supabase client in your application.

## Setup the Supabase client library[#](#setup-the-supabase-client-library)

TypeScript (Amplify)Swift (iOS)FlutterKotlin

```
123456789101112131415import { fetchAuthSession, Hub } from 'aws-amplify/auth'const supabase = createClient('https://<supabase-project>.supabase.co', 'SUPABASE_ANON_KEY', {  accessToken: async () => {    const tokens = await fetchAuthSession()    // Alternatively you can use tokens?.idToken instead.    return tokens?.accessToken  },})// if you're using Realtime you also need to set up a listener for Cognito auth changesHub.listen('auth', () => {  fetchAuthSession().then((tokens) => supabase.realtime.setAuth(tokens?.accessToken))})
```

## Add a new Third-Party Auth integration to your project[#](#add-a-new-third-party-auth-integration-to-your-project)

In the dashboard navigate to your project's [Authentication settings](https://supabase.com/dashboard/project/_/settings/auth) and find the Third-Party Auth section to add a new integration.

In the CLI add the following config to your `supabase/config.toml` file:

```
1234[auth.third_party.aws_cognito]enabled = trueuser_pool_id = "<id>"user_pool_region = "<region>"
```

## Use a pre-token generation trigger to assign the authenticated role[#](#use-a-pre-token-generation-trigger-to-assign-the-authenticated-role)

Your Supabase project inspects the `role` claim present in all JWTs sent to it, to assign the correct Postgres role when using the Data API, Storage or Realtime authorization.

By default, Amazon Cognito JWTs (both ID token and access tokens) do not contain a `role` claim in them. If you were to send such a JWT to your Supabase project, the `anon` role would be assigned when executing the Postgres query. Most of your app's logic will be accessible by the `authenticated` role.

A recommended approach to do this is to configure a [Pre-Token Generation Trigger](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html) either `V1_0` (ID token only) or `V2_0` (both access and ID token). To do this you will need to create a new Lambda function (in any language and runtime) and assign it to the [Amazon Cognito User Pool's Lambda Triggers configuration](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-working-with-aws-lambda-triggers.html). For example, the Lambda function should look similar to this:

Node.js

```
1234567891011export const handler = async (event) => {  event.response = {    claimsOverrideDetails: {      claimsToAddOrOverride: {        role: 'authenticated',      },    },  }  return event}
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/third-party/aws-cognito.mdx)

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