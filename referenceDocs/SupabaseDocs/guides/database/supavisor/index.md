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

3.  Debugging

5.  [Supavisor](https://supabase.com/docs/guides/database/supavisor)

# 

Supavisor

## 

Troubleshooting Supavisor errors

* * *

Supavisor logs are available under [Pooler Logs](https://supabase.com/dashboard/project/_/logs/pooler-logs) in the Dashboard. The following are common errors and their solutions:

| Error Type | Description | Resolution Link |
| --- | --- | --- |
| Max client connections reached | This error happens when the number of connections to Supavisor is more than [the allowed limit of your compute add-on](https://supabase.com/docs/guides/platform/compute-add-ons). | Follow this [guide](https://github.com/orgs/supabase/discussions/22305) to resolve. |
| Connection failed `{:error, :eaddrnotavail}` to 'db.xxx.supabase.co':5432 | Supavisor cannot connect to the customer database. This is usually caused if the target database is unable to respond. | N/A |
| Connection failed `{:error, :nxdomain}` to 'db.xxx.supabase.co':5432 | Supavisor cannot connect to the customer database. This is usually caused if the target database is unable to respond. | N/A |
| Connection closed when state was authentication | This error happens when either the database doesn’t exist or if the user doesn't have the right credentials. | N/A |
| Subscribe error: `{:error, :worker_not_found}` | This log event is emitted when the client tries to connect to the database, but Supavisor does not have the necessary information to route the connection. Try reconnecting to the database as it can take some time for the project information to propagate to Supavisor. | N/A |
| Subscribe error: `{:error, {:badrpc, {:error, {:erpc, :timeout}}}}` | This is a timeout error when the communication between different Supavisor nodes takes longer than expected. Try reconnecting to the database. | N/A |
| Terminating with reason :client\_termination when state was :busy | This error happens when the client terminates the connection before the connection with the database is completed. | N/A |
| Error: received invalid response to GSSAPI negotiation: S | This error happens due to `gssencmode` parameter not set to disabled. | Follow this [guide](https://github.com/orgs/supabase/discussions/30173) to resolve. |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/supavisor.mdx)

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