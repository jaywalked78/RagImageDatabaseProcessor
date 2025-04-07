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

5.  [S3 Uploads](https://supabase.com/docs/guides/storage/uploads/s3-uploads)

# 

S3 Uploads

## 

Learn how to upload files to Supabase Storage using S3.

* * *

You can use the S3 protocol to upload files to Supabase Storage. To get started with S3, see the [S3 setup guide](https://supabase.com/docs/guides/storage/s3/authentication).

The S3 protocol supports file upload using:

-   A single request
-   Multiple requests via Multipart Upload

## Single request uploads[#](#single-request-uploads)

The `PutObject` action uploads the file in a single request. This matches the behavior of the Supabase SDK [Standard Upload](https://supabase.com/docs/guides/storage/uploads/standard-uploads).

Use `PutObject` to upload smaller files, where retrying the entire upload won't be an issue. The maximum file size on paid plans is 50 GB.

For example, using JavaScript and the `aws-sdk` client:

```
1234567891011121314import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'const s3Client = new S3Client({...})const file = fs.createReadStream('path/to/file')const uploadCommand = new PutObjectCommand({  Bucket: 'bucket-name',  Key: 'path/to/file',  Body: file,  ContentType: 'image/jpeg',})await s3Client.send(uploadCommand)
```

## Multipart uploads[#](#multipart-uploads)

Multipart Uploads split the file into smaller parts and upload them in parallel, maximizing the upload speed on a fast network. When uploading large files, this allows you to retry the upload of individual parts in case of network issues.

This method is preferable over [Resumable Upload](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) for server-side uploads, when you want to maximize upload speed at the cost of resumability. The maximum file size on paid plans is 50 GB.

### Upload a file in parts[#](#upload-a-file-in-parts)

Use the `Upload` class from an S3 client to upload a file in parts. For example, using JavaScript:

```
123456789101112131415import { S3Client } from '@aws-sdk/client-s3'import { Upload } from '@aws-sdk/lib-storage'const s3Client = new S3Client({...})const file = fs.createReadStream('path/to/very-large-file')const upload = new Upload(s3Client, {  Bucket: 'bucket-name',  Key: 'path/to/file',  ContentType: 'image/jpeg',  Body: file,})await uploader.done()
```

### Aborting multipart uploads[#](#aborting-multipart-uploads)

All multipart uploads are automatically aborted after 24 hours. To abort a multipart upload before that, you can use the [`AbortMultipartUpload`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_AbortMultipartUpload.html) action.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/uploads/s3-uploads.mdx)

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