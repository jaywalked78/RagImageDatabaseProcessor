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

3.  Uploads

5.  [Limits](https://supabase.com/docs/guides/storage/uploads/file-limits)

# 

Limits

## 

Learn how to increase Supabase file limits.

* * *

## Global file size[#](#global-file-size)

You can set the max file size across all your buckets by setting this global value in the dashboard [here](https://supabase.com/dashboard/project/_/settings/storage). For Free projects, the limit can't exceed 50 MB. On the Pro Plan and up, you can set this value to up to 50 GB. If you need more than 50 GB, [contact us](https://supabase.com/dashboard/support/new).

| Plan | Max File Size Limit |
| --- | --- |
| Free | 50 MB |
| Pro | 50 GB |
| Team | 50 GB |
| Enterprise | Custom |

This option is a global limit, which applies to all your buckets.

Additionally, you can specify the max file size on a per [bucket level](https://supabase.com/docs/guides/storage/buckets/creating-buckets#restricting-uploads) but it can't be higher than this global limit. As a good practice, the global limit should be set to the highest possible file size that your application accepts, and apply per bucket limits.

## Per bucket restrictions[#](#per-bucket-restrictions)

You can have different restrictions on a per bucket level such as restricting the file types (e.g. `pdf`, `images`, `videos`) or the max file size, which should be lower than the global limit. To apply these limit on a bucket level see [Creating Buckets](https://supabase.com/docs/guides/storage/buckets/creating-buckets#restricting-uploads).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/uploads/file-limits.mdx)

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