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

3.  Debugging

5.  [Testing your Edge Functions](https://supabase.com/docs/guides/functions/unit-test)

# 

Testing your Edge Functions

## 

Writing Unit Tests for Edge Functions using Deno Test

* * *

Testing is an essential step in the development process to ensure the correctness and performance of your Edge Functions.

## Testing in Deno[#](#testing-in-deno)

Deno has a built-in test runner that you can use for testing JavaScript or TypeScript code. You can read the [official documentation](https://docs.deno.com/runtime/manual/basics/testing/) for more information and details about the available testing functions.

## Folder structure[#](#folder-structure)

We recommend creating your testing in a `supabase/functions/tests` directory, using the same name as the Function followed by `-test.ts`:

```
12345678910└── supabase    ├── functions    │   ├── function-one    │   │   └── index.ts    │   └── function-two    │   │   └── index.ts    │   └── tests    │       └── function-one-test.ts  # Tests for function-one    │       └── function-two-test.ts  # Tests for function-two    └── config.toml
```

## Example script[#](#example-script)

The following script is a good example to get started with testing your Edge Functions:

```
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061// Import required libraries and modulesimport { assert, assertEquals } from 'https://deno.land/std@0.192.0/testing/asserts.ts'import { createClient, SupabaseClient } from 'jsr:@supabase/supabase-js@2'// Will load the .env file to Deno.envimport 'https://deno.land/x/dotenv@v3.2.2/load.ts'// Set up the configuration for the Supabase clientconst supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY') ?? ''const options = {  auth: {    autoRefreshToken: false,    persistSession: false,    detectSessionInUrl: false,  },}// Test the creation and functionality of the Supabase clientconst testClientCreation = async () => {  var client: SupabaseClient = createClient(supabaseUrl, supabaseKey, options)  // Verify if the Supabase URL and key are provided  if (!supabaseUrl) throw new Error('supabaseUrl is required.')  if (!supabaseKey) throw new Error('supabaseKey is required.')  // Test a simple query to the database  const { data: table_data, error: table_error } = await client    .from('my_table')    .select('*')    .limit(1)  if (table_error) {    throw new Error('Invalid Supabase client: ' + table_error.message)  }  assert(table_data, 'Data should be returned from the query.')}// Test the 'hello-world' functionconst testHelloWorld = async () => {  var client: SupabaseClient = createClient(supabaseUrl, supabaseKey, options)  // Invoke the 'hello-world' function with a parameter  const { data: func_data, error: func_error } = await client.functions.invoke('hello-world', {    body: { name: 'bar' },  })  // Check for errors from the function invocation  if (func_error) {    throw new Error('Invalid response: ' + func_error.message)  }  // Log the response from the function  console.log(JSON.stringify(func_data, null, 2))  // Assert that the function returned the expected result  assertEquals(func_data.message, 'Hello bar!')}// Register and run the testsDeno.test('Client Creation Test', testClientCreation)Deno.test('Hello-world Function Test', testHelloWorld)
```

This test case consists of two parts. The first part tests the client library and verifies that the database can be connected to and returns values from a table (`my_table`). The second part tests the edge function and checks if the received value matches the expected value. Here's a brief overview of the code:

-   We import various testing functions from the Deno standard library, including `assert`, `assertExists`, and `assertEquals`.
-   We import the `createClient` and `SupabaseClient` classes from the `@supabase/supabase-js` library to interact with the Supabase client.
-   We define the necessary configuration for the Supabase client, including the Supabase URL, API key, and authentication options.
-   The `testClientCreation` function tests the creation of a Supabase client instance and queries the database for data from a table. It verifies that data is returned from the query.
-   The `testHelloWorld` function tests the "Hello-world" Edge Function by invoking it using the Supabase client's `functions.invoke` method. It checks if the response message matches the expected greeting.
-   We run the tests using the `Deno.test` function, providing a descriptive name for each test case and the corresponding test function.

Make sure to replace the placeholders (`supabaseUrl`, `supabaseKey`, `my_table`) with the actual values relevant to your Supabase setup.

## Running Edge Functions locally[#](#running-edge-functions-locally)

To locally test and debug Edge Functions, you can utilize the Supabase CLI. Let's explore how to run Edge Functions locally using the Supabase CLI:

1.  Ensure that the Supabase server is running by executing the following command:
    
    ```
    1supabase start
    ```
    
2.  In your terminal, use the following command to serve the Edge Functions locally:
    
    ```
    1supabase functions serve
    ```
    
    This command starts a local server that runs your Edge Functions, enabling you to test and debug them in a development environment.
    
3.  Create the environment variables file:
    
    ```
    12345678# creates the filetouch .env# adds the SUPABASE_URL secretecho "SUPABASE_URL=http://localhost:54321" >> .env# adds the SUPABASE_ANON_KEY secretecho "SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0" >> .env# Alternatively, you can open it in your editor:open .env
    ```
    
4.  To run the tests, use the following command in your terminal:
    
    ```
    1deno test --allow-all supabase/functions/tests/function-one-test.ts
    ```
    

## Resources[#](#resources)

-   Full guide on Testing Supabase Edge Functions on [Mansueli's tips](https://blog.mansueli.com/testing-supabase-edge-functions-with-deno-test)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/unit-test.mdx)

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