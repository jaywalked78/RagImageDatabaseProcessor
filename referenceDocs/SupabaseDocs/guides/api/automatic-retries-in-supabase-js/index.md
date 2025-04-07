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

REST API

# 

How to do automatic retries with `supabase-js`

## 

Learn how to add automatic retries to your Supabase API requests using `fetch-retry`.

* * *

##### Important

You should only enable retries if your requests fail with network errors (e.g. 520 status from Cloudflare). A high number of retries have the potential to exhaust the Data API connection pool, which could result in lower throughput and failed requests.

The `fetch-retry` package allows you to add retry logic to `fetch` requests, making it a useful tool for enhancing the resilience of API calls in your Supabase applications. Here's a step-by-step guide on how to integrate `fetch-retry` with the `supabase-js` library.

## 1\. Install dependencies[#](#1-install-dependencies)

To get started, ensure you have both `supabase-js` and `fetch-retry` installed in your project:

```
1npm install @supabase/supabase-js fetch-retry
```

## 2\. Wrap the fetch function[#](#2-wrap-the-fetch-function)

The `fetch-retry` package works by wrapping the native `fetch` function. You can create a custom fetch instance with retry logic and pass it to the `supabase-js` client.

```
123456789101112import { createClient } from '@supabase/supabase-js'import fetchRetry from 'fetch-retry'// Wrap the global fetch with fetch-retryconst fetchWithRetry = fetchRetry(fetch)// Create a Supabase client instance with the custom fetchconst supabase = createClient('https://your-supabase-url.supabase.co', 'your-anon-key', {  global: {    fetch: fetchWithRetry,  },})
```

## 3\. Configure retry options[#](#3-configure-retry-options)

You can configure `fetch-retry` options to control retry behavior, such as the number of retries, retry delay, and which errors should trigger a retry.

Here is an example with custom retry options:

```
12345const fetchWithRetry = fetchRetry(fetch, {  retries: 3, // Number of retry attempts  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000), // Exponential backoff  retryOn: [520], // Retry only on Cloudflare errors})
```

In this example, the `retryDelay` function implements an exponential backoff strategy, and retries are triggered only for specific HTTP status codes.

## 4\. Using the Supabase client[#](#4-using-the-supabase-client)

With `fetch-retry` integrated, you can use the Supabase client as usual. The retry logic will automatically apply to all network requests made by `supabase-js`.

```
1234567891011async function fetchData() {  const { data, error } = await supabase.from('your_table').select('*')  if (error) {    console.error('Error fetching data:', error)  } else {    console.log('Fetched data:', data)  }}fetchData()
```

## 5\. Fine-Tuning retries for specific requests[#](#5-fine-tuning-retries-for-specific-requests)

If you need different retry logic for certain requests, you can use the `retryOn` with a custom function to inspect the URL or response and decide whether to retry the request.

```
12345678910111213141516171819202122232425262728293031const fetchWithRetry = fetchRetry(fetch, {  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),  retryOn: (attempt, error, response) => {    const shouldRetry      = (attempt: number, error: Error | null, response: Response | null) =>        attempt < 3          && response          && response.status == 520 // Cloudflare errors          && response.url.includes('rpc/your_stored_procedure')    if (shouldRetry(attempt, error, response)) {      console.log(`Retrying request... Attempt #${attempt}`, response)      return true    }    return false  }})async function yourStoredProcedure() {  const { data, error } = await supabase    .rpc('your_stored_procedure', { param1: 'value1' });  if (error) {    console.log('Error executing RPC:', error);  } else {    console.log('Response:', data);  }}yourStoredProcedure();
```

By using `retryOn` with a custom function, you can define specific conditions for retrying requests. In this example, the retry logic is applied only to requests targeting a specific stored procedure.

## Conclusion[#](#conclusion)

Integrating `fetch-retry` with `supabase-js` is a straightforward way to add robustness to your Supabase API requests. By handling transient errors and implementing retry strategies, you can improve the reliability of your application while maintaining a seamless user experience.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/api/automatic-retries-in-supabase-js.mdx)

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