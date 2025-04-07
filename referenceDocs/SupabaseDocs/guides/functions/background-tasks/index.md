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

3.  Guides

5.  [Background Tasks](https://supabase.com/docs/guides/functions/background-tasks)

# 

Background Tasks

## 

How to run background tasks in an Edge Function outside of the request handler

* * *

Edge Function instances can process background tasks outside of the request handler. Background tasks are useful for asynchronous operations like uploading a file to Storage, updating a database, or sending events to a logging service. You can respond to the request immediately and leave the task running in the background.

### How it works[#](#how-it-works)

You can use `EdgeRuntime.waitUntil(promise)` to explicitly mark background tasks. The Function instance continues to run until the promise provided to `waitUntil` completes.

The maximum duration is capped based on the wall-clock, CPU, and memory limits. The Function will shutdown when it reaches one of these [limits](https://supabase.com/docs/guides/functions/limits).

You can listen to the `beforeunload` event handler to be notified when Function invocation is about to be shut down.

### Example[#](#example)

Here's an example of using `EdgeRuntime.waitUntil` to run a background task and using `beforeunload` event to be notified when the instance is about to be shut down.

```
1234567891011121314151617181920async function longRunningTask() {  // do work here}// Mark the longRunningTask's returned promise as a background task.// note: we are not using await because we don't want it to block.EdgeRuntime.waitUntil(longRunningTask())// Use beforeunload event handler to be notified when function is about to shutdownaddEventListener('beforeunload', (ev) => {  console.log('Function will be shutdown due to', ev.detail?.reason)  // save state or log the current progress})// Invoke the function using a HTTP request.// This will start the background taskDeno.serve(async (req) => {  return new Response('ok')})
```

### Starting a background task in the request handler[#](#starting-a-background-task-in-the-request-handler)

You can call `EdgeRuntime.waitUntil` in the request handler too. This will not block the request.

```
123456789101112async function fetchAndLog(url: string) {  const response = await fetch(url)  console.log(response)}Deno.serve(async (req) => {  // this will not block the request,  // instead it will run in the background  EdgeRuntime.waitUntil(fetchAndLog('https://httpbin.org/json'))  return new Response('ok')})
```

### Testing background tasks locally[#](#testing-background-tasks-locally)

When testing Edge Functions locally with Supabase CLI, the instances are terminated automatically after a request is completed. This will prevent background tasks from running to completion.

To prevent that, you can update the `supabase/config.toml` with the following settings:

```
12[edge_runtime]policy = "per_worker"
```

When running with `per_worker` policy, Function won't auto-reload on edits. You will need to manually restart it by running `supabase functions serve`.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/background-tasks.mdx)

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