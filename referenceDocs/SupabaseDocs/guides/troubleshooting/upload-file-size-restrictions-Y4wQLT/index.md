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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Upload file size restrictions

Last edited: 1/15/2025

* * *

You can view the max permissible upload size for your plan in the [docs](https://supabase.com/docs/guides/storage/uploads/file-limits).

## There are two ways to control the max upload sizes:[#](#there-are-two-ways-to-control-the-max-upload-sizes)

The first way is through the [global storage settings](https://supabase.com/dashboard/project/_/settings/storage):

![Screenshot 2024-06-20 at 7 06 57 PM](https://github.com/supabase/supabase/assets/91111415/c33acc4a-efd8-4746-ac98-ddc71e17f8f1)

The second way is at the [bucket level](https://supabase.com/dashboard/project/_/storage/buckets/)

1.  Edit a bucket's configurations:
    
    ![Screenshot 2024-06-20 at 7 07 48 PM](https://github.com/supabase/supabase/assets/91111415/51719d9f-3644-40ed-9aaa-8b21fff41634)
2.  Change the file upload restriction if set:
    
    ![Screenshot 2024-06-20 at 7 07 56 PM](https://github.com/supabase/supabase/assets/91111415/917f3cf6-81c4-444f-9ac1-f26eec5eac0c)

## Different upload methods impose file size restrictions:[#](#different-upload-methods-impose-file-size-restrictions)

-   [Standard uploads can only transfer up to 5GBs](https://supabase.com/docs/guides/storage/uploads/standard-uploads?queryGroups=language&language=js). However, for files above 6MB, the below methods are more performant and reliable
-   [Resumable](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) and [S3](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) uploads can support transfers up to 50GB in size.

## Metadata

* * *

### Products

[Storage](https://supabase.com/docs/guides/troubleshooting?products=storage)

* * *

### Tags

[upload](https://supabase.com/docs/guides/troubleshooting?tags=upload)[file](https://supabase.com/docs/guides/troubleshooting?tags=file)[size](https://supabase.com/docs/guides/troubleshooting?tags=size)[restriction](https://supabase.com/docs/guides/troubleshooting?tags=restriction)

* * *

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