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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  Platform Configuration

5.  [SSL Enforcement](https://supabase.com/docs/guides/platform/ssl-enforcement)

# 

Postgres SSL Enforcement

* * *

Your Supabase project supports connecting to the Postgres DB without SSL enabled to maximize client compatibility. For increased security, you can prevent clients from connecting if they're not using SSL.

Disabling SSL enforcement only applies to connections to Postgres and Supavisor ("Connection Pooler"); all HTTP APIs offered by Supabase (e.g., PostgREST, Storage, Auth) automatically enforce SSL on all incoming connections.

Projects need to be at least on Postgres 13.3.0 to enable SSL enforcement. You can find the Postgres version of your project in the [Infrastructure Settings page](https://supabase.com/dashboard/project/_/settings/infrastructure). If your project is on an older version, you will need to [upgrade](https://supabase.com/docs/guides/platform/migrating-and-upgrading-projects#upgrade-your-project) to use this feature.

## Manage SSL enforcement via the dashboard[#](#manage-ssl-enforcement-via-the-dashboard)

SSL enforcement can be configured via the "Enforce SSL on incoming connections" setting under the SSL Configuration section in [Database Settings page](https://supabase.com/dashboard/project/_/settings/database) of the dashboard.

## Manage SSL enforcement via the CLI[#](#manage-ssl-enforcement-via-the-cli)

To get started:

1.  [Install](https://supabase.com/docs/guides/cli) the Supabase CLI 1.37.0+.
2.  [Log in](https://supabase.com/docs/guides/getting-started/local-development#log-in-to-the-supabase-cli) to your Supabase account using the CLI.
3.  Ensure that you have [Owner or Admin permissions](https://supabase.com/docs/guides/platform/access-control#manage-team-members) for the project that you are enabling SSL enforcement.

### Check enforcement status[#](#check-enforcement-status)

You can use the `get` subcommand of the CLI to check whether SSL is currently being enforced:

```
1supabase ssl-enforcement --project-ref {ref} get --experimental
```

Response if SSL is being enforced:

```
1SSL is being enforced.
```

Response if SSL is not being enforced:

```
1SSL is *NOT* being enforced.
```

### Update enforcement[#](#update-enforcement)

The `update` subcommand is used to change the SSL enforcement status for your project:

```
1supabase ssl-enforcement --project-ref {ref} update --enable-db-ssl-enforcement --experimental
```

Similarly, to disable SSL enforcement:

```
1supabase ssl-enforcement --project-ref {ref} update --disable-db-ssl-enforcement --experimental
```

### A note about Postgres SSL modes[#](#a-note-about-postgres-ssl-modes)

Postgres supports [multiple SSL modes](https://www.postgresql.org/docs/current/libpq-ssl.html#LIBPQ-SSL-PROTECTION) on the client side. These modes provide different levels of protection. Depending on your needs, it is important to verify that the SSL mode in use is performing the required level of enforcement and verification of SSL connections.

The strongest mode offered by Postgres is `verify-full` and this is the mode you most likely want to use when SSL enforcement is enabled. To use `verify-full` you will need to download the Supabase CA certificate for your database. The certificate is available through the dashboard under the SSL Configuration section in the [Database Settings page](https://supabase.com/dashboard/project/_/settings/database).

Once the CA certificate has been downloaded, add it to the certificate authority list used by Postgres.

```
1cat {location of downloaded prod-ca-2021.crt} >> ~/.postgres/root.crt
```

With the CA certificate added to the trusted certificate authorities list, use `psql` or your client library to connect to Supabase:

```
1psql "postgresql://aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=verify-full" -U postgres.<user>
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/ssl-enforcement.mdx)

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