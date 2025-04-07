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

3.  Security

5.  [Rate Limits](https://supabase.com/docs/guides/auth/rate-limits)

# 

Rate limits

## 

Rate limits protect your services from abuse

* * *

Supabase Auth enforces rate limits on endpoints to prevent abuse. Some rate limits are [customizable](https://supabase.com/dashboard/project/_/auth/rate-limits).

| Endpoint | Path | Limited By | Rate Limit |
| --- | --- | --- | --- |
| All endpoints that send emails | `/auth/v1/signup` `/auth/v1/recover` `/auth/v1/user`[1](#user-content-fn-1) | Sum of combined requests | Defaults to 4 emails per hour as of 14th July 2023. As of 21 Oct 2023, this has been updated to 2 emails per hour. You can only change this with your own custom SMTP setup. |
| All endpoints that send One-Time-Passwords (OTP) | `/auth/v1/otp` | Sum of combined requests | Defaults to 30 OTPs per hour. Is customizable. |
| Send OTPs or magic links | `/auth/v1/otp` | Last request | Defaults to 60 seconds window before a new request is allowed. Is customizable. |
| Signup confirmation request | `/auth/v1/signup` | Last request | Defaults to 60 seconds window before a new request is allowed. Is customizable. |
| Password Reset Request | `/auth/v1/recover` | Last request | Defaults to 60 seconds window before a new request is allowed. Is customizable. |
| Verification requests | `/auth/v1/verify` | IP Address | 360 requests per hour (with bursts up to 30 requests) |
| Token refresh requests | `/auth/v1/token` | IP Address | 1800 requests per hour (with bursts up to 30 requests) |
| Create or Verify an MFA challenge | `/auth/v1/factors/:id/challenge` `/auth/v1/factors/:id/verify` | IP Address | 15 requests per hour (with bursts up to requests) |
| Anonymous sign-ins | `/auth/v1/signup`[2](#user-content-fn-2) | IP Address | 30 requests per hour (with bursts up to 30 requests) |

## Footnotes[#](#footnote-label)

1.  The rate limit is only applied on `/auth/v1/user` if this endpoint is called to update the user's email address. [↩](#user-content-fnref-1)
    
2.  The rate limit is only applied on `/auth/v1/signup` if this endpoint is called without passing in an email or phone number in the request body. [↩](#user-content-fnref-2)
    

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/rate-limits.mdx)

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