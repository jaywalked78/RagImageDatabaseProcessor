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

5.  [Firebase Auth](https://supabase.com/docs/guides/auth/third-party/firebase-auth)

# 

Firebase Auth

## 

Use Firebase Auth with your Supabase project

* * *

Firebase Auth can be used as a third-party authentication provider alongside Supabase Auth, or standalone, with your Supabase project.

## Getting started[#](#getting-started)

1.  First you need to add an integration to connect your Supabase project with your Firebase project. You will need to get the Project ID in the [Firebase Console](https://console.firebase.google.com/u/0/project/_/settings/general).
2.  Add a new Third-party Auth integration in your project's [Authentication settings](https://supabase.com/dashboard/project/_/settings/auth).
3.  If you are using Third Party Auth when self hosting, create and attach restrictive RLS policies to all tables in your public schema, Storage and Realtime to **prevent unauthorized access from unrelated Firebase projects**.
4.  Assign the `role: 'authenticated'` [custom user claim](https://firebase.google.com/docs/auth/admin/custom-claims) to all your users.
5.  Finally set up the Supabase client in your application.

## Setup the Supabase client library[#](#setup-the-supabase-client-library)

TypeScriptFlutterSwift (iOS)Kotlin (Android)Kotlin (Multiplatform)

Creating a client for the Web is as easy as passing the `accessToken` async function. This function should [return the Firebase Auth JWT of the current user](https://firebase.google.com/docs/auth/admin/verify-id-tokens#web) (or null if no such user) is found.

```
1234567import { createClient } from '@supabase/supabase-js'const supabase = createClient('https://<supabase-project>.supabase.co', 'SUPABASE_ANON_KEY', {  accessToken: async () => {    return (await firebase.auth().currentUser?.getIdToken(/* forceRefresh */ false)) ?? null  },})
```

Make sure the all users in your application have the `role: 'authenticated'` [custom claim](https://firebase.google.com/docs/auth/admin/custom-claims) set. If you're using the `onCreate` Cloud Function to add this custom claim to newly signed up users, you will need to call `getIdToken(/* forceRefresh */ true)` immediately after sign up as the `onCreate` function does not run synchronously.

## Add a new Third-Party Auth integration to your project[#](#add-a-new-third-party-auth-integration-to-your-project)

In the dashboard navigate to your project's [Authentication settings](https://supabase.com/dashboard/project/_/settings/auth) and find the Third-Party Auth section to add a new integration.

In the CLI add the following config to your `supabase/config.toml` file:

```
123[auth.third_party.firebase]enabled = trueproject_id = "<id>"
```

## Adding an extra layer of security to your project's RLS policies (self-hosting only)[#](#adding-an-extra-layer-of-security-to-your-projects-rls-policies-self-hosting-only)

**Follow this section carefully to prevent unauthorized access to your project's data when self-hosting.**

When using the Supabase hosted platform, following this step is optional.

Firebase Auth uses a single set of JWT signing keys for all projects. This means that JWTs issued from an unrelated Firebase project to yours could access data in your Supabase project.

When using the Supabase hosted platform, JWTs coming from Firebase project IDs you have not registered will be rejected before they reach your database. When self-hosting implementing this mechanism is your responsibility. An easy way to guard against this is to create and maintain the following RLS policies for **all of your tables in the `public` schema**. You should also attach this policy to [Storage](https://supabase.com/docs/guides/storage/security/access-control) buckets or [Realtime](https://supabase.com/docs/guides/realtime/authorization) channels.

It's recommended you use a [restrictive Postgres Row-Level Security policy](https://www.postgresql.org/docs/current/sql-createpolicy.html).

Restrictive RLS policies differ from regular (or permissive) policies in that they use the `as restrictive` clause when being defined. They do not grant permissions, but rather restrict any existing or future permissions. They're great for cases like this where the technical limitations of Firebase Auth remain separate from your app's logic.

Postgres has two types of policies: permissive and restrictive. This example uses restrictive policies so make sure you don't omit the `as restrictive` clause.

This is an example of such an RLS policy that will restrict access to only your project's (denoted with `<firebase-project-id>`) users, and not any other Firebase project.

```
12345678910111213create policy "Restrict access to Supabase Auth and Firebase Auth for project ID <firebase-project-id>"  on table_name  as restrictive  to authenticated  using (    (auth.jwt()->>'iss' = 'https://<project-ref>.supabase.co/auth/v1')    or    (        auth.jwt()->>'iss' = 'https://securetoken.google.com/<firebase-project-id>'        and        auth.jwt()->>'aud' = '<firebase-project-id>'     )  );
```

If you have a lot of tables in your app, or need to manage complex RLS policies for [Storage](https://supabase.com/docs/guides/storage) or [Realtime](https://supabase.com/docs/guides/realtime) it can be useful to define a [stable Postgres function](https://www.postgresql.org/docs/current/xfunc-volatility.html) that performs the check to cut down on duplicate code. For example:

```
1234567891011121314create function public.is_supabase_or_firebase_project_jwt()  returns bool  language sql  stable  returns null on null input  return (    (auth.jwt()->>'iss' = 'https://<project-ref>.supabase.co/auth/v1')    or    (        auth.jwt()->>'iss' = concat('https://securetoken.google.com/<firebase-project-id>')        and        auth.jwt()->>'aud' = '<firebase-project-id>'     )  );
```

Make sure you substitute `<project-ref>` with your Supabase project's ID and the `<firebase-project-id>` to your Firebase Project ID. Then the restrictive policies on all your tables, buckets and channels can be simplified to be:

```
12345create policy "Restrict access to correct Supabase and Firebase projects"  on table_name  as restrictive  to authenticated  using ((select public.is_supabase_or_firebase_project_jwt()) is true);
```

## Assign the "role" custom claim[#](#assign-the-role-custom-claim)

Your Supabase project inspects the `role` claim present in all JWTs sent to it, to assign the correct Postgres role when using the Data API, Storage or Realtime authorization.

By default, Firebase JWTs do not contain a `role` claim in them. If you were to send such a JWT to your Supabase project, the `anon` role would be assigned when executing the Postgres query. Most of your app's logic will be accessible by the `authenticated` role.

### Use Firebase Authentication functions to assign the authenticated role[#](#use-firebase-authentication-functions-to-assign-the-authenticated-role)

You have two choices to set up a Firebase Authentication function depending on your Firebase project's configuration:

1.  Easiest: Use a [blocking Firebase Authentication function](https://firebase.google.com/docs/auth/extend-with-blocking-functions) but this is only available if your project uses [Firebase Authentication with Identity Platform](https://cloud.google.com/security/products/identity-platform).
2.  Manually assign the custom claims to all users with the [admin SDK](https://firebase.google.com/docs/auth/admin/custom-claims#set_and_validate_custom_user_claims_via_the_admin_sdk) and define an [`onCreate` Firebase Authentication Cloud Function](https://firebase.google.com/docs/auth/extend-with-functions) to persist the role to all newly created users.

Node.js (Blocking Functions Gen 2)Python (Blocking Functions Gen 2)onCreate Cloud Function in Node.js

```
123456789101112131415161718192021import { beforeUserCreated, beforeUserSignedIn } from 'firebase-functions/v2/identity'export const beforecreated = beforeUserCreated((event) => {  return {    customClaims: {      // The Supabase project will use this role to assign the `authenticated`      // Postgres role.      role: 'authenticated',    },  }})export const beforesignedin = beforeUserSignedIn((event) => {  return {    customClaims: {      // The Supabase project will use this role to assign the `authenticated`      // Postgres role.      role: 'authenticated',    },  }})
```

Note that instead of using `customClaims` you can instead use `sessionClaims`. The difference is that `session_claims` are not saved in the Firebase user profile, but remain valid for as long as the user is signed in.

Finally deploy your functions for the changes to take effect:

```
1firebase deploy --only functions
```

Note that these functions are only called on new sign-ups and sign-ins. Existing users will not have these claims in their ID tokens. You will need to use the admin SDK to assign the role custom claim to all users. Make sure you do this after the blocking Firebase Authentication functions as described above are deployed.

### Use the admin SDK to assign the role custom claim to all users[#](#use-the-admin-sdk-to-assign-the-role-custom-claim-to-all-users)

You need to run a script that will assign the `role: 'authenticated'` custom claim to all of your existing Firebase Authentication users. You can do this by combining the [list users](https://firebase.google.com/docs/auth/admin/manage-users#list_all_users) and [set custom user claims](https://firebase.google.com/docs/auth/admin/create-custom-tokens) admin APIs. An example script is provided below:

```
1234567891011121314151617181920212223242526'use strict';const { initializeApp } = require('firebase-admin/app');const { getAuth } = require('firebase-admin/auth');initializeApp();async function setRoleCustomClaim() => {  let nextPageToken = undefined  do {    const listUsersResult = await getAuth().listUsers(1000, nextPageToken)    nextPageToken = listUsersResult.pageToken    await Promise.all(listUsersResult.users.map(async (userRecord) => {      try {        await getAuth().setCustomUserClaims(userRecord.id, {          role: 'authenticated'        })      } catch (error) {        console.error('Failed to set custom role for user', userRecord.id)      }    })  } while (nextPageToken);};setRoleCustomClaim().then(() => process.exit(0))
```

After all users have received the `role: 'authenticated'` claim, it will appear in all newly issued ID tokens for the user.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/third-party/firebase-auth.mdx)

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