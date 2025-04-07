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

Realtime

1.  [Realtime](https://supabase.com/docs/guides/realtime)

3.  Debugging

5.  [Operational Error Codes](https://supabase.com/docs/guides/realtime/error_codes)

# 

Operational Error Codes

## 

List of operational codes to help understand your deployment and usage.

* * *

| Code | Description | Action |
| --- | --- | --- |
| `RealtimeDisabledForConfiguration` | The configuration provided to Realtime on connect will not be able to provide you any Postgres Changes | Verify your configuration on channel startup as you might not have your tables properly registered |
| `TenantNotFound` | The tenant you are trying to connect to does not exist | Verify the tenant name you are trying to connect to exists in the realtime.tenants table |
| `ErrorConnectingToWebSocket` | Error when trying to connect to the WebSocket server | Verify user information on connect |
| `ErrorAuthorizingWebSocket` | Error when trying to authorize the WebSocket connection | Verify user information on connect |
| `TableHasSpacesInName` | The table you are trying to listen to has spaces in its name which we are unable to support | Change the table name to not have spaces in it |
| `UnableToDeleteTenant` | Error when trying to delete a tenant | Contact Support |
| `UnableToSetPolicies` | Error when setting up Authorization Policies | Contact Support |
| `UnableCheckoutConnection` | Error when trying to checkout a connection from the tenant pool | Contact Support |
| `UnableToSubscribeToPostgres` | Error when trying to subscribe to Postgres changes | Contact Support |
| `ChannelRateLimitReached` | The number of channels you can create has reached its limit | Contact support to increase your rate limits |
| `ConnectionRateLimitReached` | The number of connected clients as reached its limit | Contact support to increase your rate limits |
| `ClientJoinRateLimitReached` | The rate of joins per second from your clients as reached the channel limits | Contact support to increase your rate limits |
| `UnableToConnectToTenantDatabase` | Realtime was not able to connect to the tenant's database | Contact support for further instructions |
| `RealtimeNodeDisconnected` | Realtime is a distributed application and this means that one the system is unable to communicate with one of the distributed nodes | Contact support for further instructions |
| `MigrationsFailedToRun` | Error when running the migrations against the Tenant database that are required by Realtime | Contact support for further instructions |
| `ErrorStartingPostgresCDCStream` | Error when starting the Postgres CDC stream which is used for Postgres Changes | Contact support for further instructions |
| `UnknownDataProcessed` | An unknown data type was processed by the Realtime system | Contact support for further instructions |
| `ErrorStartingPostgresCDC` | Error when starting the Postgres CDC extension which is used for Postgres Changes | Contact support for further instructions |
| `ReplicationSlotBeingUsed` | The replication slot is being used by another transaction | Contact support for further instructions |
| `PoolingReplicationPreparationError` | Error when preparing the replication slot | Contact support for further instructions |
| `PoolingReplicationError` | Error when pooling the replication slot | Contact support for further instructions |
| `SubscriptionDeletionFailed` | Error when trying to delete a subscription for Postgres changes | Contact support for further instructions |
| `UnableToDeletePhantomSubscriptions` | Error when trying to delete subscriptions that are no longer being used | Contact support for further instructions |
| `UnableToCheckProcessesOnRemoteNode` | Error when trying to check the processes on a remote node | Contact support for further instructions |
| `UnableToCreateCounter` | Error when trying to create a counter to track rate limits for a tenant | Contact support for further instructions |
| `UnableToIncrementCounter` | Error when trying to increment a counter to track rate limits for a tenant | Contact support for further instructions |
| `UnableToDecrementCounter` | Error when trying to decrement a counter to track rate limits for a tenant | Contact support for further instructions |
| `UnableToUpdateCounter` | Error when trying to update a counter to track rate limits for a tenant | Contact support for further instructions |
| `UnableToFindCounter` | Error when trying to find a counter to track rate limits for a tenant | Contact support for further instructions |
| `UnhandledProcessMessage` | Unhandled message received by a Realtime process | Contact support for further instructions |
| `UnknownError` | An unknown error occurred | Contact support for further instructions |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/realtime/error_codes.mdx)

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