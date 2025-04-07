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

Storage

1.  [Storage](https://supabase.com/docs/guides/storage)

3.  S3

5.  [Authentication](https://supabase.com/docs/guides/storage/s3/authentication)

# 

S3 Authentication

## 

Learn about authenticating with Supabase Storage S3.

* * *

You have two options to authenticate with Supabase Storage S3:

-   Using the generated S3 access keys from your [project settings](https://supabase.com/dashboard/project/_/settings/storage) (Intended exclusively for server-side use)
-   Using a Session Token, which will allow you to authenticate with a user JWT token and provide limited access via Row Level Security (RLS).

## S3 access keys[#](#s3-access-keys)

##### Keep these credentials secure

S3 access keys provide full access to all S3 operations across all buckets and bypass RLS policies. These are meant to be used only on the server.

To authenticate with S3, generate a pair of credentials (Access Key ID and Secret Access Key), copy the endpoint and region from the [project settings page](https://supabase.com/dashboard/project/_/settings/storage).

This is all the information you need to connect to Supabase Storage using any S3-compatible service.

![Storage S3 Access keys](https://supabase.com/docs/img/storage/s3-credentials.png)

aws-sdk-jsAWS Credentials

```
1234567891011import { S3Client } from '@aws-sdk/client-s3';const client = new S3Client({  forcePathStyle: true,  region: 'project_region',  endpoint: 'https://project_ref.supabase.co/storage/v1/s3',  credentials: {    accessKeyId: 'your_access_key_id',    secretAccessKey: 'your_secret_access_key',  }})
```

## Session token[#](#session-token)

You can authenticate to Supabase S3 with a user JWT token to provide limited access via RLS to all S3 operations. This is useful when you want initialize the S3 client on the server scoped to a specific user, or use the S3 client directly from the client side.

All S3 operations performed with the Session Token are scoped to the authenticated user. RLS policies on the Storage Schema are respected.

To authenticate with S3 using a Session Token, use the following credentials:

-   access\_key\_id: `project_ref`
-   secret\_access\_key: `anonKey`
-   session\_token: `valid jwt token`

For example, using the `aws-sdk` library:

```
12345678910111213141516import { S3Client } from '@aws-sdk/client-s3'const {  data: { session },} = await supabase.auth.getSession()const client = new S3Client({  forcePathStyle: true,  region: 'project_region',  endpoint: 'https://project_ref.supabase.co/storage/v1/s3',  credentials: {    accessKeyId: 'project_ref',    secretAccessKey: 'anonKey',    sessionToken: session.access_token,  },})
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/s3/authentication.mdx)

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