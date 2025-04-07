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

5.  [API Compatibility](https://supabase.com/docs/guides/storage/s3/compatibility)

# 

S3 Compatibility

## 

Learn about the compatibility of Supabase Storage with S3.

* * *

Supabase Storage is compatible with the S3 protocol. You can use any S3 client to interact with your Storage objects.

Storage supports [standard](https://supabase.com/docs/guides/storage/uploads/standard-uploads), [resumable](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) and [S3 uploads](https://supabase.com/docs/guides/storage/uploads/s3-uploads) and all these protocols are interoperable. You can upload a file with the S3 protocol and list it with the REST API or upload with Resumable uploads and list with S3.

Storage supports presigning a URL using query parameters. Specifically, Supabase Storage expects requests to be made using [AWS Signature Version 4](https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-query-string-auth.html). To enable this feature, enable the S3 connection via S3 protocol in the Settings page for Supabase Storage.

The S3 protocol is currently in Public Alpha. If you encounter any issues or have feature requests, [contact us](https://supabase.com/dashboard/support/new).

## Implemented endpoints[#](#implemented-endpoints)

The most commonly used endpoints are implemented, and more will be added. Implemented S3 endpoints are marked with ✅ in the following tables.

### Bucket operations[#](#bucket-operations)

| API Name | Feature |
| --- | --- |
| ✅ [ListBuckets](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBuckets.html) |  |
| ✅ [HeadBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadBucket.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) | ❌ ACL:  
❌ x-amz-acl  
❌ x-amz-grant-full-control  
❌ x-amz-grant-read  
❌ x-amz-grant-read-acp  
❌ x-amz-grant-write  
❌ x-amz-grant-write-acp  
❌ Object Locking:  
❌ x-amz-bucket-object-lock-enabled  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [DeleteBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucket.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [GetBucketLocation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [DeleteBucketCors](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucketCors.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [GetBucketEncryption](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketEncryption.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [GetBucketLifecycleConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLifecycleConfiguration.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [GetBucketCors](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketCors.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [PutBucketCors](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketCors.html) | ❌ Checksums:  
❌ x-amz-sdk-checksum-algorithm  
❌ x-amz-checksum-algorithm  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ❌ [PutBucketLifecycleConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html) | ❌ Checksums:  
❌ x-amz-sdk-checksum-algorithm  
❌ x-amz-checksum-algorithm  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |

### Object operations[#](#object-operations)

| API Name | Feature |
| --- | --- |
| ✅ [HeadObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html) | ✅ Conditional Operations:  
✅ If-Match  
✅ If-Modified-Since  
✅ If-None-Match  
✅ If-Unmodified-Since  
✅ Range:  
✅ Range (has no effect in HeadObject)  
✅ partNumber  
❌ SSE-C:  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [ListObjects](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjects.html) | Query Parameters:  
✅ delimiter  
✅ encoding-type  
✅ marker  
✅ max-keys  
✅ prefix  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) | Query Parameters:  
✅ list-type  
✅ continuation-token  
✅ delimiter  
✅ encoding-type  
✅ fetch-owner  
✅ max-keys  
✅ prefix  
✅ start-after  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html) | ✅ Conditional Operations:  
✅ If-Match  
✅ If-Modified-Since  
✅ If-None-Match  
✅ If-Unmodified-Since  
✅ Range:  
✅ Range  
✅ PartNumber  
❌ SSE-C:  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) | System Metadata:  
✅ Content-Type  
✅ Cache-Control  
✅ Content-Disposition  
✅ Content-Encoding  
✅ Content-Language  
✅ Expires  
❌ Content-MD5  
❌ Object Lifecycle  
❌ Website:  
❌ x-amz-website-redirect-location  
❌ SSE-C:  
❌ x-amz-server-side-encryption  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ x-amz-server-side-encryption-aws-kms-key-id  
❌ x-amz-server-side-encryption-context  
❌ x-amz-server-side-encryption-bucket-key-enabled  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Tagging:  
❌ x-amz-tagging  
❌ Object Locking:  
❌ x-amz-object-lock-mode  
❌ x-amz-object-lock-retain-until-date  
❌ x-amz-object-lock-legal-hold  
❌ ACL:  
❌ x-amz-acl  
❌ x-amz-grant-full-control  
❌ x-amz-grant-read  
❌ x-amz-grant-read-acp  
❌ x-amz-grant-write-acp  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) | ❌ Multi-factor authentication:  
❌ x-amz-mfa  
❌ Object Locking:  
❌ x-amz-bypass-governance-retention  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [DeleteObjects](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjects.html) | ❌ Multi-factor authentication:  
❌ x-amz-mfa  
❌ Object Locking:  
❌ x-amz-bypass-governance-retention  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [ListMultipartUploads](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListMultipartUploads.html) | ✅ Query Parameters:  
✅ delimiter  
✅ encoding-type  
✅ key-marker  
✅️ max-uploads  
✅ prefix  
✅ upload-id-marker |
| ✅ [CreateMultipartUpload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateMultipartUpload.html) | ✅ System Metadata:  
✅ Content-Type  
✅ Cache-Control  
✅ Content-Disposition  
✅ Content-Encoding  
✅ Content-Language  
✅ Expires  
❌ Content-MD5  
❌ Website:  
❌ x-amz-website-redirect-location  
❌ SSE-C:  
❌ x-amz-server-side-encryption  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ x-amz-server-side-encryption-aws-kms-key-id  
❌ x-amz-server-side-encryption-context  
❌ x-amz-server-side-encryption-bucket-key-enabled  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Tagging:  
❌ x-amz-tagging  
❌ Object Locking:  
❌ x-amz-object-lock-mode  
❌ x-amz-object-lock-retain-until-date  
❌ x-amz-object-lock-legal-hold  
❌ ACL:  
❌ x-amz-acl  
❌ x-amz-grant-full-control  
❌ x-amz-grant-read  
❌ x-amz-grant-read-acp  
❌ x-amz-grant-write-acp  
❌ Storage class:  
❌ x-amz-storage-class  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [CompleteMultipartUpload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html) | ❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner  
❌ Request Payer:  
❌ x-amz-request-payer |
| ✅ [AbortMultipartUpload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_AbortMultipartUpload.html) | ❌ Request Payer:  
❌ x-amz-request-payer |
| ✅ [CopyObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CopyObject.html) | ✅ Operation Metadata:  
⚠️ x-amz-metadata-directive  
✅ System Metadata:  
✅ Content-Type  
✅ Cache-Control  
✅ Content-Disposition  
✅ Content-Encoding  
✅ Content-Language  
✅ Expires  
✅ Conditional Operations:  
✅ x-amz-copy-source  
✅ x-amz-copy-source-if-match  
✅ x-amz-copy-source-if-modified-since  
✅ x-amz-copy-source-if-none-match  
✅ x-amz-copy-source-if-unmodified-since  
❌ ACL:  
❌ x-amz-acl  
❌ x-amz-grant-full-control  
❌ x-amz-grant-read  
❌ x-amz-grant-read-acp  
❌ x-amz-grant-write-acp  
❌ Website:  
❌ x-amz-website-redirect-location  
❌ SSE-C:  
❌ x-amz-server-side-encryption  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ x-amz-server-side-encryption-aws-kms-key-id  
❌ x-amz-server-side-encryption-context  
❌ x-amz-server-side-encryption-bucket-key-enabled  
❌ x-amz-copy-source-server-side-encryption-customer-algorithm  
❌ x-amz-copy-source-server-side-encryption-customer-key  
❌ x-amz-copy-source-server-side-encryption-customer-key-MD5  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Tagging:  
❌ x-amz-tagging  
❌ x-amz-tagging-directive  
❌ Object Locking:  
❌ x-amz-object-lock-mode  
❌ x-amz-object-lock-retain-until-date  
❌ x-amz-object-lock-legal-hold  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner  
❌ x-amz-source-expected-bucket-owner  
❌ Checksums:  
❌ x-amz-checksum-algorithm |
| ✅ [UploadPart](https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPart.html) | ✅ System Metadata:  
❌ Content-MD5  
❌ SSE-C:  
❌ x-amz-server-side-encryption  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |
| ✅ [UploadPartCopy](https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPartCopy.html) | ❌ Conditional Operations:  
❌ x-amz-copy-source  
❌ x-amz-copy-source-if-match  
❌ x-amz-copy-source-if-modified-since  
❌ x-amz-copy-source-if-none-match  
❌ x-amz-copy-source-if-unmodified-since  
✅ Range:  
✅ x-amz-copy-source-range  
❌ SSE-C:  
❌ x-amz-server-side-encryption-customer-algorithm  
❌ x-amz-server-side-encryption-customer-key  
❌ x-amz-server-side-encryption-customer-key-MD5  
❌ x-amz-copy-source-server-side-encryption-customer-algorithm  
❌ x-amz-copy-source-server-side-encryption-customer-key  
❌ x-amz-copy-source-server-side-encryption-customer-key-MD5  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner  
❌ x-amz-source-expected-bucket-owner |
| ✅ [ListParts](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListParts.html) | Query Parameters:  
✅ max-parts  
✅ part-number-marker  
❌ Request Payer:  
❌ x-amz-request-payer  
❌ Bucket Owner:  
❌ x-amz-expected-bucket-owner |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/s3/compatibility.mdx)

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