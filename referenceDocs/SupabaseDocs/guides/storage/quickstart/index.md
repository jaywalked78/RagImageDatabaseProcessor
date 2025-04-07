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

3.  [Quickstart](https://supabase.com/docs/guides/storage/quickstart)

# 

Storage Quickstart

## 

Learn how to use Supabase to store and serve files.

* * *

This guide shows the basic functionality of Supabase Storage. Find a full [example application on GitHub](https://github.com/supabase/supabase/tree/master/examples/user-management/nextjs-user-management).

## Concepts[#](#concepts)

Supabase Storage consists of Files, Folders, and Buckets.

### Files[#](#files)

Files can be any sort of media file. This includes images, GIFs, and videos. It is best practice to store files outside of your database because of their sizes. For security, HTML files are returned as plain text.

### Folders[#](#folders)

Folders are a way to organize your files (just like on your computer). There is no right or wrong way to organize your files. You can store them in whichever folder structure suits your project.

### Buckets[#](#buckets)

Buckets are distinct containers for files and folders. You can think of them like "super folders". Generally you would create distinct buckets for different Security and Access Rules. For example, you might keep all video files in a "video" bucket, and profile pictures in an "avatar" bucket.

File, Folder, and Bucket names **must follow** [AWS object key naming guidelines](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html) and avoid use of any other characters.

## Create a bucket[#](#create-a-bucket)

You can create a bucket using the Supabase Dashboard. Since the storage is interoperable with your Postgres database, you can also use SQL or our client libraries. Here we create a bucket called "avatars":

DashboardSQLJavaScriptDartSwiftPython

1.  Go to the [Storage](https://supabase.com/dashboard/project/_/storage/buckets) page in the Dashboard.
2.  Click **New Bucket** and enter a name for the bucket.
3.  Click **Create Bucket**.

## Upload a file[#](#upload-a-file)

You can upload a file from the Dashboard, or within a browser using our JS libraries.

DashboardJavaScriptDart

1.  Go to the [Storage](https://supabase.com/dashboard/project/_/storage/buckets) page in the Dashboard.
2.  Select the bucket you want to upload the file to.
3.  Click **Upload File**.
4.  Select the file you want to upload.

## Download a file[#](#download-a-file)

You can download a file from the Dashboard, or within a browser using our JS libraries.

DashboardJavaScriptDartSwiftPython

1.  Go to the [Storage](https://supabase.com/dashboard/project/_/storage/buckets) page in the Dashboard.
2.  Select the bucket that contains the file.
3.  Select the file that you want to download.
4.  Click **Download**.

## Add security rules[#](#add-security-rules)

To restrict access to your files you can use either the Dashboard or SQL.

DashboardSQL

1.  Go to the [Storage](https://supabase.com/dashboard/project/_/storage/buckets) page in the Dashboard.
2.  Click **Policies** in the sidebar.
3.  Click **Add Policies** in the `OBJECTS` table to add policies for Files. You can also create policies for Buckets.
4.  Choose whether you want the policy to apply to downloads (SELECT), uploads (INSERT), updates (UPDATE), or deletes (DELETE).
5.  Give your policy a unique name.
6.  Write the policy using SQL.

* * *

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/quickstart.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FJ9mTPY8rIXE%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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