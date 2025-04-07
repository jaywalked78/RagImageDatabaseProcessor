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

Queues

1.  [Queues](https://supabase.com/docs/guides/queues)

3.  References

5.  [API](https://supabase.com/docs/guides/queues/api)

# 

API

* * *

When you create a Queue in Supabase, you can choose to create helper database functions in the `pgmq_public` schema. This schema exposes operations to manage Queue Messages to consumers client-side, but does not expose functions for creating or dropping Queues.

Database functions in `pgmq_public` can be exposed via Supabase Data API so consumers client-side can call them. Visit the [Quickstart](https://supabase.com/docs/guides/queues/quickstart) for an example.

### `pgmq_public.pop(queue_name)`[#](#pgmqpublicpopqueuename)

Retrieves the next available message and deletes it from the specified Queue.

-   `queue_name` (`text`): Queue name

* * *

### `pgmq_public.send(queue_name, message, sleep_seconds)`[#](#pgmqpublicsendqueuename-message-sleepseconds)

Adds a Message to the specified Queue, optionally delaying its visibility to all consumers by a number of seconds.

-   `queue_name` (`text`): Queue name
-   `message` (`jsonb`): Message payload to send
-   `sleep_seconds` (`integer`, optional): Delay message visibility by specified seconds. Defaults to 0

* * *

### `pgmq_public.send_batch(queue_name, messages, sleep_seconds)`[#](#pgmqpublicsendbatchqueuename-messages-sleepseconds)

Adds a batch of Messages to the specified Queue, optionally delaying their availability to all consumers by a number of seconds.

-   `queue_name` (`text`): Queue name
-   `messages` (`jsonb[]`): Array of message payloads to send
-   `sleep_seconds` (`integer`, optional): Delay messages visibility by specified seconds. Defaults to 0

* * *

### `pgmq_public.archive(queue_name, message_id)`[#](#pgmqpublicarchivequeuename-messageid)

Archives a Message by moving it from the Queue table to the Queue's archive table.

-   `queue_name` (`text`): Queue name
-   `message_id` (`bigint`): ID of the Message to archive

* * *

### `pgmq_public.delete(queue_name, message_id)`[#](#pgmqpublicdeletequeuename-messageid)

Permanently deletes a Message from the specified Queue.

-   `queue_name` (`text`): Queue name
-   `message_id` (`bigint`): ID of the Message to delete

* * *

### `pgmq_public.read(queue_name, sleep_seconds, n)`[#](#pgmqpublicreadqueuename-sleepseconds-n)

Reads up to "n" Messages from the specified Queue with an optional "sleep\_seconds" (visibility timeout).

-   `queue_name` (`text`): Queue name
-   `sleep_seconds` (`integer`): Visibility timeout in seconds
-   `n` (`integer`): Maximum number of Messages to read

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/queues/api.mdx)

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