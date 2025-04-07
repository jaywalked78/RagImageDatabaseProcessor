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

3.  Management

5.  [Copy / Move Objects](https://supabase.com/docs/guides/storage/management/copy-move-objects)

# 

Copy Objects

## 

Learn how to copy and move objects

* * *

## Copy objects[#](#copy-objects)

You can copy objects between buckets or within the same bucket. Currently only objects up to 5 GB can be copied using the API.

When making a copy of an object, the owner of the new object will be the user who initiated the copy operation.

### Copying objects within the same bucket[#](#copying-objects-within-the-same-bucket)

To copy an object within the same bucket, use the `copy` method.

```
1await supabase.storage.from('avatars').copy('public/avatar1.png', 'private/avatar2.png')
```

### Copying objects across buckets[#](#copying-objects-across-buckets)

To copy an object across buckets, use the `copy` method and specify the destination bucket.

```
123await supabase.storage.from('avatars').copy('public/avatar1.png', 'private/avatar2.png', {  destinationBucket: 'avatars2',})
```

## Move objects[#](#move-objects)

You can move objects between buckets or within the same bucket. Currently only objects up to 5GB can be moved using the API.

When moving an object, the owner of the new object will be the user who initiated the move operation. Once the object is moved, the original object will no longer exist.

### Moving objects within the same bucket[#](#moving-objects-within-the-same-bucket)

To move an object within the same bucket, you can use the `move` method.

```
123const { data, error } = await supabase.storage  .from('avatars')  .move('public/avatar1.png', 'private/avatar2.png')
```

### Moving objects across buckets[#](#moving-objects-across-buckets)

To move an object across buckets, use the `move` method and specify the destination bucket.

```
123await supabase.storage.from('avatars').move('public/avatar1.png', 'private/avatar2.png', {  destinationBucket: 'avatars2',})
```

## Permissions[#](#permissions)

For a user to move and copy objects, they need `select` permission on the source object and `insert` permission on the destination object. For example:

```
123456789101112131415create policy "User can select their own objects (in any buckets)"on storage.objectsfor selectto authenticatedusing (    owner_id = (select auth.uid()));create policy "User can upload in their own folders (in any buckets)"on storage.objectsfor insertto authenticatedwith check (    (storage.folder(name))[1] = (select auth.uid()));
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/management/copy-move-objects.mdx)

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