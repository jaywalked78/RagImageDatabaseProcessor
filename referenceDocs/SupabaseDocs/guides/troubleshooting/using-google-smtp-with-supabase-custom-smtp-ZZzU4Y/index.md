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

# Using Google SMTP with Supabase Custom SMTP

Last edited: 2/21/2025

* * *

Hey everyone, i've been hearing feedback about how challenging it can be to get google SMTP working properly with Supabase. I've tried setting this up with a trial google workspace account and this is what i've discovered.

1.  The sender email and SMTP username has to be your google workspace admin email.
2.  The SMTP password used has to be an app password. Google workspace doesn't make it easy to to figure out how to create this. You need to **enable 2FA** on your workspace account first (not inside the admin console but in [https://myaccount.google.com/](https://myaccount.google.com/))
3.  If you want to use `smtp-relay.gmail.com` only port 465 works. If you want to use `smtp.gmail.com`, you can use port 465 or 587. The following screenshots show what those steps look like:

## For `smtp-relay.gmail.com`[#](#for-smtp-relaygmailcom)

![image](https://supabase.com/docs/img/troubleshooting/800448a1-0245-4a26-855f-3be8f44adf03.png)

(The "Require TLS encryption" option didn't seem to affect anything when tested)![image](https://supabase.com/docs/img/troubleshooting/5b55ddbc-abfc-4c66-a012-b8e4d23cd438.png)

## For `smtp.gmail.com`[#](#for-smtpgmailcom)

![image](https://supabase.com/docs/img/troubleshooting/ade24c85-50b5-47ca-a2ce-c3f77a0e128a.png)

A lot of this was figured out through trial and error. This is unlikely to be a Supabase Auth bug because Supabase Auth uses the [native Golang SMTP library](https://pkg.go.dev/net/smtp) . If you still have issues setting up Google SMTP, you can try switching to one of these SMTP providers:

-   [Resend](https://resend.com/blog/how-to-configure-supabase-to-send-emails-from-your-domain)
-   [SendGrid](https://sendgrid.com/en-us)
-   [Mailgun](https://www.mailgun.com/)
-   AWS SES SMTP

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[smtp](https://supabase.com/docs/guides/troubleshooting?tags=smtp)[google](https://supabase.com/docs/guides/troubleshooting?tags=google)[workspace](https://supabase.com/docs/guides/troubleshooting?tags=workspace)[2FA](https://supabase.com/docs/guides/troubleshooting?tags=2FA)[TLS](https://supabase.com/docs/guides/troubleshooting?tags=TLS)[encryption](https://supabase.com/docs/guides/troubleshooting?tags=encryption)[port](https://supabase.com/docs/guides/troubleshooting?tags=port)

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