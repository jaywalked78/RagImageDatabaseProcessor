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

3.  Buckets

5.  [Fundamentals](https://supabase.com/docs/guides/storage/buckets/fundamentals)

# 

Storage Buckets

* * *

Buckets allow you to keep your files organized and determines the [Access Model](#access-model) for your assets. [Upload restrictions](https://supabase.com/docs/guides/storage/buckets/creating-buckets#restricting-uploads) like max file size and allowed content types are also defined at the bucket level.

## Access model[#](#access-model)

There are 2 access models for buckets, **public** and **private** buckets.

### Private buckets[#](#private-buckets)

When a bucket is set to **Private** all operations are subject to access control via [RLS policies](https://supabase.com/docs/guides/storage/security/access-control). This also applies when downloading assets. Buckets are private by default.

The only ways to download assets within a private bucket is to:

-   Use the [download method](https://supabase.com/docs/reference/javascript/storage-from-download) by providing a authorization header containing your user's JWT. The RLS policy you create on the `storage.objects` table will use this user to determine if they have access.
-   Create a signed URL with the [`createSignedUrl` method](https://supabase.com/docs/reference/javascript/storage-from-createsignedurl) that can be accessed for a limited time.

#### Example use cases:[#](#example-use-cases)

-   Uploading users' sensitive documents
-   Securing private assets by using RLS to set up fine-grain access controls

### Public buckets[#](#public-buckets)

When a bucket is designated as 'Public,' it effectively bypasses access controls for both retrieving and serving files within the bucket. This means that anyone who possesses the asset URL can readily access the file.

Access control is still enforced for other types of operations including uploading, deleting, moving, and copying.

#### Example use cases:[#](#example-use-cases)

-   User profile pictures
-   User public media
-   Blog post content

Public buckets are more performant than private buckets since they are [cached differently](https://supabase.com/docs/guides/storage/cdn/fundamentals#public-vs-private-buckets).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/buckets/fundamentals.mdx)

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