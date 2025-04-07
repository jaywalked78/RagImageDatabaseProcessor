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

# Edge Function 'wall clock time limit reached'

Last edited: 1/17/2025

* * *

**What Does "Wall Clock Time Limit Reached" Mean?**

The message "wall clock time limit reached" typically indicates that a process has reached the maximum time allowed for execution. This time is measured by a clock, similar to a system clock or a clock on the wall. It encompasses the entire duration a process takes to complete, including any periods of inactivity or waiting.

When this message appears in the context of your edge function, it means that the function has emitted a Shutdown event either after reaching the specified wall clock duration or when it hits a resource limit such as CPU time used or memory utilized.

**Current Limits Explained**

-   Wall Clock Time Limit: Currently set at 400 seconds for the total duration your edge function can run.
-   CPU Execution Time: Limited to 200 milliseconds of active computing.

This means that if your edge function completes its task within these time constraints, there's no need to be concerned about the "wall clock time limit reached" error message.

Because the "wall clock time limit reached" warning can be expected in some cases. This message is hard-coded to be printed out when the worker has been terminated, even if it hasn't reached the time limit. However, if your function terminates with this warning and returns a 546 error response, then this indicates that your function is exceeding the allowed execution time, signaling a long-running task.

**Steps to Troubleshoot** If you're facing the "wall clock time limit reached" error with a 546 error code, here are actions to take:

-   Review Your Function's Logic: Examine the operations within your edge function for any inefficiencies or prolonged processes. Consider optimizing code, minimizing unnecessary calculations, and implementing asynchronous operations where possible.
    
-   Divide Complex Tasks: For functions handling complex or extensive tasks, try breaking them down into smaller, discrete functions. This approach can help manage workloads more effectively and stay within time limits.
    
-   Monitor Execution Time: Use our logging or monitoring tools available to keep an eye on your function's performance. This can pinpoint where optimizations are necessary. To access logs visit: [Supabase Project Functions](https://app.supabase.com/project/_/functions) Select your function and click on Logs.
    
-   Check Our Guides: For more tips, refer to our debugging guide here: [Debugging Edge Functions](https://supabase.com/docs/guides/functions/debugging#logs--debugging)
    

**Future Considerations** There are plans to make the wall clock time limit configurable per project in the future. However, currently, the only way to adjust this limit is by self-hosting [Edge Functions](https://github.com/supabase/edge-runtime/).

Stay updated on changes by regularly checking our changelog [here](https://github.com/orgs/supabase/discussions/categories/changelog).

## Metadata

* * *

### Products

[Functions](https://supabase.com/docs/guides/troubleshooting?products=functions)

* * *

### Related error codes

[546](https://supabase.com/docs/guides/troubleshooting?errorCodes=546)

* * *

### Tags

[wall clock](https://supabase.com/docs/guides/troubleshooting?tags=wall+clock)[limit](https://supabase.com/docs/guides/troubleshooting?tags=limit)[time](https://supabase.com/docs/guides/troubleshooting?tags=time)[shutdown](https://supabase.com/docs/guides/troubleshooting?tags=shutdown)

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