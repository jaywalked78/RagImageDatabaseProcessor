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

Database

1.  [Database](https://supabase.com/docs/guides/database/overview)

3.  Extensions

5.  [pgsodium (pending deprecation): Encryption Features](https://supabase.com/docs/guides/database/extensions/pgsodium)

# 

pgsodium (pending deprecation): Encryption Features

* * *

Supabase DOES NOT RECOMMEND any new usage of [`pgsodium`](https://github.com/michelp/pgsodium).

The [`pgsodium`](https://github.com/michelp/pgsodium) extension is expected to go through a deprecation cycle in the near future. We will reach out to owners of impacted projects to assist with migrations away from [`pgsodium`](https://github.com/michelp/pgsodium) once the deprecation process begins.

The [Vault extension](https://supabase.com/docs/guides/database/vault) won’t be impacted. Its internal implementation will shift away from pgsodium, but the interface and API will remain unchanged.

[`pgsodium`](https://github.com/michelp/pgsodium) is a Postgres extension which provides SQL access to [`libsodium`'s](https://doc.libsodium.org/) high-level cryptographic algorithms.

Supabase previously documented two features derived from pgsodium. Namely [Server Key Management](https://github.com/michelp/pgsodium#server-key-management) and [Transparent Column Encryption](https://github.com/michelp/pgsodium#transparent-column-encryption). At this time, we do not recommend using either on the Supabase platform due to their high level of operational complexity and misconfiguration risk.

Note that Supabase projects are encrypted at rest by default which likely is sufficient for your compliance needs e.g. SOC2 & HIPAA.

## Get the root encryption key for your Supabase project[#](#get-the-root-encryption-key-for-your-supabase-project)

Encryption requires keys. Keeping the keys in the same database as the encrypted data would be unsafe. For more information about managing the `pgsodium` root encryption key on your Supabase project see **[encryption key location](https://supabase.com/docs/guides/database/vault#encryption-key-location)**. This key is required to decrypt values stored in [Supabase Vault](https://supabase.com/docs/guides/database/vault) and data encrypted with Transparent Column Encryption.

## Resources[#](#resources)

-   [Supabase Vault](https://supabase.com/docs/guides/database/vault)
-   Read more about Supabase Vault in the [blog post](https://supabase.com/blog/vault-now-in-beta)
-   [Supabase Vault on GitHub](https://github.com/supabase/vault)

## Resources[#](#resources)

-   Official [`pgsodium` documentation](https://github.com/michelp/pgsodium)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pgsodium.mdx)

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