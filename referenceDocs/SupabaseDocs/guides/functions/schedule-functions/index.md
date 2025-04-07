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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Examples

5.  [Scheduling Functions](https://supabase.com/docs/guides/functions/schedule-functions)

# 

Scheduling Edge Functions

* * *

The hosted Supabase Platform supports the [`pg_cron` extension](https://supabase.com/docs/guides/database/extensions/pgcron), a recurring job scheduler in Postgres.

In combination with the [`pg_net` extension](https://supabase.com/docs/guides/database/extensions/pgnet), this allows us to invoke Edge Functions periodically on a set schedule.

To access the auth token securely for your Edge Function call, we recommend storing them in [Supabase Vault](https://supabase.com/docs/guides/database/vault).

## Examples[#](#examples)

### Invoke an Edge Function every minute[#](#invoke-an-edge-function-every-minute)

Store `project_url` and `anon_key` in Supabase Vault:

```
12select vault.create_secret('https://project-ref.supabase.co', 'project_url');select vault.create_secret('YOUR_SUPABASE_ANON_KEY', 'anon_key');
```

Make a POST request to a Supabase Edge Function every minute:

```
12345678910111213141516select  cron.schedule(    'invoke-function-every-minute',    '* * * * *', -- every minute    $$    select      net.http_post(          url:= (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/function-name',          headers:=jsonb_build_object(            'Content-type', 'application/json',            'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'anon_key')          ),          body:=concat('{"time": "', now(), '"}')::jsonb      ) as request_id;    $$  );
```

## Resources[#](#resources)

-   [`pg_net` extension](https://supabase.com/docs/guides/database/extensions/pgnet)
-   [`pg_cron` extension](https://supabase.com/docs/guides/database/extensions/pgcron)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/schedule-functions.mdx)

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