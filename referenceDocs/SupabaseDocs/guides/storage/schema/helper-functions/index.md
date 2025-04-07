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

3.  Schema

5.  [Helper Functions](https://supabase.com/docs/guides/storage/schema/helper-functions)

# 

Storage Helper Functions

## 

Learn the storage schema

* * *

Supabase Storage provides SQL helper functions which you can use to write RLS policies.

### `storage.filename()`[#](#storagefilename)

Returns the name of a file. For example, if your file is stored in `public/subfolder/avatar.png` it would return: `'avatar.png'`

**Usage**

This example demonstrates how you would allow any user to download a file called `favicon.ico`:

```
1234567create policy "Allow public downloads"on storage.objectsfor selectto publicusing (  storage.filename(name) = 'favicon.ico');
```

### `storage.foldername()`[#](#storagefoldername)

Returns an array path, with all of the subfolders that a file belongs to. For example, if your file is stored in `public/subfolder/avatar.png` it would return: `[ 'public', 'subfolder' ]`

**Usage**

This example demonstrates how you would allow authenticated users to upload files to a folder called `private`:

```
1234567create policy "Allow authenticated uploads"on storage.objectsfor insertto authenticatedwith check (  (storage.foldername(name))[1] = 'private');
```

### `storage.extension()`[#](#storageextension)

Returns the extension of a file. For example, if your file is stored in `public/subfolder/avatar.png` it would return: `'png'`

**Usage**

This example demonstrates how you would allow restrict uploads to only PNG files inside a bucket called `cats`:

```
1234567create policy "Only allow PNG uploads"on storage.objectsfor insertto authenticatedwith check (  bucket_id = 'cats' and storage.extension(name) = 'png');
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/schema/helper-functions.mdx)

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