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

AI & Vectors

1.  [AI & Vectors](https://supabase.com/docs/guides/ai)

3.  Learn

5.  [Automatic embeddings](https://supabase.com/docs/guides/ai/automatic-embeddings)

# 

Automatic embeddings

* * *

Vector embeddings enable powerful [semantic search](https://supabase.com/docs/guides/ai/semantic-search) capabilities in Postgres, but managing them alongside your content has traditionally been complex. This guide demonstrates how to automate embedding generation and updates using Supabase [Edge Functions](https://supabase.com/docs/guides/functions), [pgmq](https://supabase.com/docs/guides/database/extensions/pgmq), [pg\_net](https://supabase.com/docs/guides/database/extensions/pg_net), and [pg\_cron](https://supabase.com/docs/guides/cron).

## Understanding the challenge[#](#understanding-the-challenge)

When implementing semantic search with pgvector, developers typically need to:

1.  Generate embeddings via an external API (like OpenAI)
2.  Store these embeddings alongside the content
3.  Keep embeddings in sync when content changes
4.  Handle failures and retries in the embedding generation process

While Postgres [full-text search](https://supabase.com/docs/guides/database/full-text-search) can handle this internally through synchronous calls to `to_tsvector` and [triggers](https://www.postgresql.org/docs/current/textsearch-features.html#TEXTSEARCH-UPDATE-TRIGGERS), semantic search requires asynchronous API calls to a provider like OpenAI to generate vector embeddings. This guide demonstrates how to use triggers, queues, and Supabase Edge Functions to bridge this gap.

## Understanding the architecture[#](#understanding-the-architecture)

We'll leverage the following Postgres and Supabase features to create the automated embedding system:

1.  [pgvector](https://supabase.com/docs/guides/database/extensions/pgvector): Stores and queries vector embeddings
2.  [pgmq](https://supabase.com/docs/guides/queues): Queues embedding generation requests for processing and retries
3.  [pg\_net](https://supabase.com/docs/guides/database/extensions/pg_net): Handles asynchronous HTTP requests to Edge Functions directly from Postgres
4.  [pg\_cron](https://supabase.com/docs/guides/cron): Automatically processes and retries embedding generations
5.  [Triggers](https://supabase.com/docs/guides/database/postgres/triggers): Detects content changes and enqueues embedding generation requests
6.  [Edge Functions](https://supabase.com/docs/guides/functions): Generates embeddings via an API like OpenAI (customizable)

We'll design the system to:

1.  Be generic, so that it can be used with any table and content. This allows you to configure embeddings in multiple places, each with the ability to customize the input used for embedding generation. These will all use the same queue infrastructure and Edge Function to generate the embeddings.
    
2.  Handle failures gracefully, by retrying failed jobs and providing detailed information about the status of each job.
    

## Implementation[#](#implementation)

We'll start by setting up the infrastructure needed to queue and process embedding generation requests. Then we'll create an example table with triggers to enqueue these embedding requests whenever content is inserted or updated.

### Step 1: Enable extensions[#](#step-1-enable-extensions)

First, let's enable the required extensions:

SQLDashboard

```
12345678910111213141516171819202122-- For vector operationscreate extension if not exists vectorwith  schema extensions;-- For queueing and processing jobs-- (pgmq will create its own schema)create extension if not exists pgmq;-- For async HTTP requestscreate extension if not exists pg_netwith  schema extensions;-- For scheduled processing and retries-- (pg_cron will create its own schema)create extension if not exists pg_cron;-- For clearing embeddings during updatescreate extension if not exists hstorewith  schema extensions;
```

Even though the SQL code is `create extension`, this is the equivalent of "enabling the extension". To disable an extension, call `drop extension`.

### Step 2: Create utility functions[#](#step-2-create-utility-functions)

Before we set up our embedding logic, we need to create some utility functions:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566-- Schema for utility functionscreate schema util;-- Utility function to get the Supabase project URL (required for Edge Functions)create function util.project_url()returns textlanguage plpgsqlsecurity defineras $$declare  secret_value text;begin  -- Retrieve the project URL from Vault  select decrypted_secret into secret_value from vault.decrypted_secrets where name = 'project_url';  return secret_value;end;$$;-- Generic function to invoke any Edge Functioncreate or replace function util.invoke_edge_function(  name text,  body jsonb,  timeout_milliseconds int = 5 * 60 * 1000  -- default 5 minute timeout)returns voidlanguage plpgsqlas $$declare  headers_raw text;  auth_header text;begin  -- If we're in a PostgREST session, reuse the request headers for authorization  headers_raw := current_setting('request.headers', true);  -- Only try to parse if headers are present  auth_header := case    when headers_raw is not null then      (headers_raw::json->>'authorization')    else      null  end;  -- Perform async HTTP request to the edge function  perform net.http_post(    url => util.project_url() || '/functions/v1/' || name,    headers => jsonb_build_object(      'Content-Type', 'application/json',      'Authorization', auth_header    ),    body => body,    timeout_milliseconds => timeout_milliseconds  );end;$$;-- Generic trigger function to clear a column on updatecreate or replace function util.clear_column()returns triggerlanguage plpgsql as $$declare    clear_column text := TG_ARGV[0];begin    NEW := NEW #= hstore(clear_column, NULL);    return NEW;end;$$;
```

Here we create:

-   A schema `util` to store utility functions.
-   A function to retrieve the Supabase project URL from [Vault](https://supabase.com/docs/guides/database/vault). We'll add this secret next.
-   A generic function to invoke any Edge Function with a given name and request body.
-   A generic trigger function to clear a column on update. This function accepts the column name as an argument and sets it to `NULL` in the `NEW` record. We'll explain how to use this function later.

Every project has a unique API URL that is required to invoke Edge Functions. Let's go ahead and add the project URL secret to Vault depending on your environment.

When working with a local Supabase stack, add the following to your `supabase/seed.sql` file:

```
12select  vault.create_secret('http://api.supabase.internal:8000', 'project_url');
```

When deploying to the cloud platform, open the [SQL editor](https://supabase.com/dashboard/project/_/sql/new) and run the following, replacing `<project-url>` with your [project's API URL](https://supabase.com/dashboard/project/_/settings/api):

```
12select  vault.create_secret('<project-url>', 'project_url');
```

### Step 3: Create queue and triggers[#](#step-3-create-queue-and-triggers)

Our goal is to automatically generate embeddings whenever content is inserted or updated within a table. We can use triggers and queues to achieve this. Our approach is to automatically queue embedding jobs whenever records are inserted or updated in a table, then process them asynchronously using a cron job. If a job fails, it will remain in the queue and be retried in the next scheduled task.

First we create a `pgmq` queue for processing embedding requests:

```
12-- Queue for processing embedding jobsselect pgmq.create('embedding_jobs');
```

Next we create a trigger function to queue embedding jobs. We'll use this function to handle both insert and update events:

```
12345678910111213141516171819202122-- Generic trigger function to queue embedding jobscreate or replace function util.queue_embeddings()returns triggerlanguage plpgsqlas $$declare  content_function text = TG_ARGV[0];  embedding_column text = TG_ARGV[1];begin  perform pgmq.send(    queue_name => 'embedding_jobs',    msg => jsonb_build_object(      'id', NEW.id,      'schema', TG_TABLE_SCHEMA,      'table', TG_TABLE_NAME,      'contentFunction', content_function,      'embeddingColumn', embedding_column    )  );  return NEW;end;$$;
```

Our `util.queue_embeddings` trigger function is generic and can be used with any table and content function. It accepts two arguments:

1.  `content_function`: The name of a function that returns the text content to be embedded. The function should accept a single row as input and return text (see the `embedding_input` example).
    
    This allows you to customize the text input passed to the embedding model - for example, you could concatenate multiple columns together like `title` and `content` and use the result as input.
    
2.  `embedding_column`: The name of the destination column where the embedding will be stored.
    

Note that the `util.queue_embeddings` trigger function requires a `for each row` clause to work correctly. See [Usage](#usage) for an example of how to use this trigger function with your table.

Next we'll create a function to process the embedding jobs. This function will read jobs from the queue, group them into batches, and invoke the Edge Function to generate embeddings. We'll use `pg_cron` to schedule this function to run every 10 seconds.

```
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758-- Function to process embedding jobs from the queuecreate or replace function util.process_embeddings(  batch_size int = 10,  max_requests int = 10,  timeout_milliseconds int = 5 * 60 * 1000 -- default 5 minute timeout)returns voidlanguage plpgsqlas $$declare  job_batches jsonb[];  batch jsonb;begin  with    -- First get jobs and assign batch numbers    numbered_jobs as (      select        message || jsonb_build_object('jobId', msg_id) as job_info,        (row_number() over (order by 1) - 1) / batch_size as batch_num      from pgmq.read(        queue_name => 'embedding_jobs',        vt => timeout_milliseconds / 1000,        qty => max_requests * batch_size      )    ),    -- Then group jobs into batches    batched_jobs as (      select        jsonb_agg(job_info) as batch_array,        batch_num      from numbered_jobs      group by batch_num    )  -- Finally aggregate all batches into array  select array_agg(batch_array)  from batched_jobs  into job_batches;  -- Invoke the embed edge function for each batch  foreach batch in array job_batches loop    perform util.invoke_edge_function(      name => 'embed',      body => batch,      timeout_milliseconds => timeout_milliseconds    );  end loop;end;$$;-- Schedule the embedding processingselect  cron.schedule(    'process-embeddings',    '10 seconds',    $$    select util.process_embeddings();    $$  );
```

Let's discuss some common questions about this approach:

#### Why not generate all embeddings in a single Edge Function request?[#](#why-not-generate-all-embeddings-in-a-single-edge-function-request)

While this is possible, it can lead to long processing times and potential timeouts. Batching allows us to process multiple embeddings concurrently and handle failures more effectively.

#### Why not one request per row?[#](#why-not-one-request-per-row)

This approach can lead to API rate limiting and performance issues. Batching provides a balance between efficiency and reliability.

#### Why queue requests instead of processing them immediately?[#](#why-queue-requests-instead-of-processing-them-immediately)

Queuing allows us to handle failures gracefully, retry requests, and manage concurrency more effectively. Specifically we are using `pgmq`'s visibility timeouts to ensure that failed requests are retried.

#### How do visibility timeouts work?[#](#how-do-visibility-timeouts-work)

Every time we read a message from the queue, we set a visibility timeout which tells `pgmq` to hide the message from other readers for a certain period. If the Edge Function fails to process the message within this period, the message becomes visible again and will be retried by the next scheduled task.

#### How do we handle retries?[#](#how-do-we-handle-retries)

We use `pg_cron` to schedule a task that reads messages from the queue and processes them. If the Edge Function fails to process a message, it becomes visible again after a timeout and can be retried by the next scheduled task.

#### Is 10 seconds a good interval for processing?[#](#is-10-seconds-a-good-interval-for-processing)

This interval is a good starting point, but you may need to adjust it based on your workload and the time it takes to generate embeddings. You can adjust the `batch_size`, `max_requests`, and `timeout_milliseconds` parameters to optimize performance.

### Step 4: Create the Edge Function[#](#step-4-create-the-edge-function)

Finally we'll create the Edge Function to generate embeddings. We'll use OpenAI's API in this example, but you can replace it with any other embedding generation service.

Use the Supabase CLI to create a new Edge Function:

```
1supabase functions new embed
```

This will create a new directory `supabase/functions/embed` with an `index.ts` file. Replace the contents of this file with the following:

_supabase/functions/embed/index.ts_:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127128129130131132133134135136137138139140141142143144145146147148149150151152153154155156157158159160161162163164165166167168169170171172173174175176177178179180181182183184185186187188189190191192193194195196// Setup type definitions for built-in Supabase Runtime APIsimport 'jsr:@supabase/functions-js/edge-runtime.d.ts'// We'll use the OpenAI API to generate embeddingsimport OpenAI from 'jsr:@openai/openai'import { z } from 'npm:zod'// We'll make a direct Postgres connection to update the documentimport postgres from 'https://deno.land/x/postgresjs@v3.4.5/mod.js'// Initialize OpenAI clientconst openai = new OpenAI({  // We'll need to manually set the `OPENAI_API_KEY` environment variable  apiKey: Deno.env.get('OPENAI_API_KEY'),})// Initialize Postgres clientconst sql = postgres(  // `SUPABASE_DB_URL` is a built-in environment variable  Deno.env.get('SUPABASE_DB_URL')!)const jobSchema = z.object({  jobId: z.number(),  id: z.number(),  schema: z.string(),  table: z.string(),  contentFunction: z.string(),  embeddingColumn: z.string(),})const failedJobSchema = jobSchema.extend({  error: z.string(),})type Job = z.infer<typeof jobSchema>type FailedJob = z.infer<typeof failedJobSchema>type Row = {  id: string  content: unknown}const QUEUE_NAME = 'embedding_jobs'// Listen for HTTP requestsDeno.serve(async (req) => {  if (req.method !== 'POST') {    return new Response('expected POST request', { status: 405 })  }  if (req.headers.get('content-type') !== 'application/json') {    return new Response('expected json body', { status: 400 })  }  // Use Zod to parse and validate the request body  const parseResult = z.array(jobSchema).safeParse(await req.json())  if (parseResult.error) {    return new Response(`invalid request body: ${parseResult.error.message}`, {      status: 400,    })  }  const pendingJobs = parseResult.data  // Track jobs that completed successfully  const completedJobs: Job[] = []  // Track jobs that failed due to an error  const failedJobs: FailedJob[] = []  async function processJobs() {    let currentJob: Job | undefined    while ((currentJob = pendingJobs.shift()) !== undefined) {      try {        await processJob(currentJob)        completedJobs.push(currentJob)      } catch (error) {        failedJobs.push({          ...currentJob,          error: error instanceof Error ? error.message : JSON.stringify(error),        })      }    }  }  try {    // Process jobs while listening for worker termination    await Promise.race([processJobs(), catchUnload()])  } catch (error) {    // If the worker is terminating (e.g. wall clock limit reached),    // add pending jobs to fail list with termination reason    failedJobs.push(      ...pendingJobs.map((job) => ({        ...job,        error: error instanceof Error ? error.message : JSON.stringify(error),      }))    )  }  // Log completed and failed jobs for traceability  console.log('finished processing jobs:', {    completedJobs: completedJobs.length,    failedJobs: failedJobs.length,  })  return new Response(    JSON.stringify({      completedJobs,      failedJobs,    }),    {      // 200 OK response      status: 200,      // Custom headers to report job status      headers: {        'content-type': 'application/json',        'x-completed-jobs': completedJobs.length.toString(),        'x-failed-jobs': failedJobs.length.toString(),      },    }  )})/** * Generates an embedding for the given text. */async function generateEmbedding(text: string) {  const response = await openai.embeddings.create({    model: 'text-embedding-3-small',    input: text,  })  const [data] = response.data  if (!data) {    throw new Error('failed to generate embedding')  }  return data.embedding}/** * Processes an embedding job. */async function processJob(job: Job) {  const { jobId, id, schema, table, contentFunction, embeddingColumn } = job  // Fetch content for the schema/table/row combination  const [row]: [Row] = await sql`    select      id,      ${sql(contentFunction)}(t) as content    from      ${sql(schema)}.${sql(table)} t    where      id = ${id}  `  if (!row) {    throw new Error(`row not found: ${schema}.${table}/${id}`)  }  if (typeof row.content !== 'string') {    throw new Error(`invalid content - expected string: ${schema}.${table}/${id}`)  }  const embedding = await generateEmbedding(row.content)  await sql`    update      ${sql(schema)}.${sql(table)}    set      ${sql(embeddingColumn)} = ${JSON.stringify(embedding)}    where      id = ${id}  `  await sql`    select pgmq.delete(${QUEUE_NAME}, ${jobId}::bigint)  `}/** * Returns a promise that rejects if the worker is terminating. */function catchUnload() {  return new Promise((reject) => {    addEventListener('beforeunload', (ev: any) => {      reject(new Error(ev.detail?.reason))    })  })}
```

The Edge Function listens for incoming HTTP requests from `pg_net` and processes each embedding job. It is a generic worker that can handle embedding jobs for any table and column. It uses OpenAI's API to generate embeddings and updates the corresponding row in the database. It also deletes the job from the queue once it has been processed.

The function is designed to process multiple jobs independently. If one job fails, it will not affect the processing of other jobs. The function returns a `200 OK` response with a list of completed and failed jobs. We can use this information to diagnose failed jobs. See [Troubleshooting](#troubleshooting) for more details.

You will need to set the `OPENAI_API_KEY` environment variable to authenticate with OpenAI. When running the Edge Function locally, you can add it to a `.env` file:

_.env_:

```
1OPENAI_API_KEY=your-api-key
```

When you're ready to deploy the Edge Function, set can set the environment variable using the Supabase CLI:

```
1supabase secrets set --env-file .env
```

or

```
1supabase secrets set OPENAI_API_KEY=<your-api-key>
```

Alternatively, you can replace the `generateEmbedding` function with your own embedding generation logic.

See [Deploy to Production](https://supabase.com/docs/guides/functions/deploy) for more information on how to deploy the Edge Function.

## Usage[#](#usage)

Now that the infrastructure is in place, let's go through an example of how to use this system to automatically generate embeddings for a table of documents. You can use this approach with multiple tables and customize the input for each embedding generation as needed.

### 1\. Create table to store documents with embeddings[#](#1-create-table-to-store-documents-with-embeddings)

We'll set up a new `documents` table that will store our content and embeddings:

```
1234567891011-- Table to store documents with embeddingscreate table documents (  id integer primary key generated always as identity,  title text not null,  content text not null,  embedding halfvec(1536),  created_at timestamp with time zone default now());-- Index for vector search over document embeddingscreate index on documents using hnsw (embedding halfvec_cosine_ops);
```

Our `documents` table stores the title and content of each document along with its vector embedding. We use a `halfvec(1536)` column to store the embeddings.

`halfvec` is a `pgvector` data type that stores float values in half precision (16 bits) to save space. Our Edge Function used OpenAI's `text-embedding-3-small` model which generates 1536-dimensional embeddings, so we use the same dimensionality here. Adjust this based on the number of dimensions your embedding model generates.

We use an [HNSW index](https://supabase.com/docs/guides/ai/vector-indexes/hnsw-indexes) on the vector column. Note that we are choosing `halfvec_cosine_ops` as the index method, which means our future queries will need to use cosine distance (`<=>`) to find similar embeddings. Also note that HNSW indexes support a maximum of 4000 dimensions for `halfvec` vectors, so keep this in mind when choosing an embedding model. If your model generates embeddings with more than 4000 dimensions, you will need to reduce the dimensionality before indexing them. See [Matryoshka embeddings](https://supabase.com/blog/matryoshka-embeddings) for a potential solution to shortening dimensions.

Also note that the table must have a primary key column named `id` for our triggers to work correctly with the `util.queue_embeddings` function and for our Edge Function to update the correct row.

### 2\. Create triggers to enqueue embedding jobs[#](#2-create-triggers-to-enqueue-embedding-jobs)

Now we'll set up the triggers to enqueue embedding jobs whenever content is inserted or updated:

```
12345678910111213141516171819202122232425-- Customize the input for embedding generation-- e.g. Concatenate title and content with a markdown headercreate or replace function embedding_input(doc documents)returns textlanguage plpgsqlimmutableas $$begin  return '# ' || doc.title || E'\n\n' || doc.content;end;$$;-- Trigger for insert eventscreate trigger embed_documents_on_insert  after insert  on documents  for each row  execute function util.queue_embeddings('embedding_input', 'embedding');-- Trigger for update eventscreate trigger embed_documents_on_update  after update of title, content -- must match the columns in embedding_input()  on documents  for each row  execute function util.queue_embeddings('embedding_input', 'embedding');
```

We create 2 triggers:

1.  `embed_documents_on_insert`: Enqueues embedding jobs whenever new rows are inserted into the `documents` table.
    
2.  `embed_documents_on_update`: Enqueues embedding jobs whenever the `title` or `content` columns are updated in the `documents` table.
    

Both of these triggers use the same `util.queue_embeddings` function that will queue the embedding jobs for processing. They accept 2 arguments:

1.  `embedding_input`: The name of the function that generates the input for embedding generation. This function allows you to customize the text input passed to the embedding model (e.g. concatenating the title and content). The function should accept a single row as input and return text.
    
2.  `embedding`: The name of the destination column where the embedding will be stored.
    

Note that the update trigger only fires when the `title` or `content` columns are updated. This is to avoid unnecessary updates to the embedding column when other columns are updated. Make sure that these columns match the columns used in the `embedding_input` function.

#### (Optional) Clearing embeddings on update[#](#optional-clearing-embeddings-on-update)

Note that our trigger will enqueue new embedding jobs when content is updated, but it will not clear any existing embeddings. This means that an embedding can be temporarily out of sync with the content until the new embedding is generated and updated.

If it is more important to have _accurate_ embeddings than _any_ embedding, you can add another trigger to clear the existing embedding until the new one is generated:

```
123456-- Trigger to clear the embedding column on updatecreate trigger clear_document_embedding_on_update  before update of title, content -- must match the columns in embedding_input()  on documents  for each row  execute function util.clear_column('embedding');
```

`util.clear_column` is a generic trigger function we created earlier that can be used to clear any column in a table.

-   It accepts the column name as an argument. This column must be nullable.
-   It requires a `before` trigger with a `for each row` clause.
-   It requires the `hstore` extension we created earlier.

This example will clear the `embedding` column whenever the `title` or `content` columns are updated (note the `of title, content` clause). This ensures that the embedding is always in sync with the title and content, but it will result in temporary gaps in search results until the new embedding is generated.

We intentionally use a `before` trigger because it allows us to modify the record before it's written to disk, avoiding an extra `update` statement that would be needed with an `after` trigger.

### 3\. Insert and update documents[#](#3-insert-and-update-documents)

Let's insert a new document and update its content to see the embedding generation in action:

```
123456789-- Insert a new documentinsert into documents (title, content)values  ('Understanding Vector Databases', 'Vector databases are specialized...');-- Immediately check the embedding columnselect id, embeddingfrom documentswhere title = 'Understanding Vector Databases';
```

You should observe that the `embedding` column is initially `null` after inserting the document. This is because the embedding generation is asynchronous and will be processed by the Edge Function in the next scheduled task.

Wait up to 10 seconds for the next task to run, then check the `embedding` column again:

```
123select id, embeddingfrom documentswhere title = 'Understanding Vector Databases';
```

You should see the generated embedding for the document.

Next let's update the content of the document:

```
123456789-- Update the content of the documentupdate documentsset content = 'Vector databases allow you to query...'where title = 'Understanding Vector Databases';-- Immediately check the embedding columnselect id, embeddingfrom documentswhere title = 'Understanding Vector Databases';
```

You should observe that the `embedding` column is reset to `null` after updating the content. This is because of the trigger we added to clear existing embeddings whenever the content is updated. The embedding will be regenerated by the Edge Function in the next scheduled task.

Wait up to 10 seconds for the next task to run, then check the `embedding` column again:

```
123select id, embeddingfrom documentswhere title = 'Understanding Vector Databases';
```

You should see the updated embedding for the document.

Finally we'll update the title of the document:

```
1234-- Update the title of the documentupdate documentsset title = 'Understanding Vector Databases with Supabase'where title = 'Understanding Vector Databases';
```

You should observe that the `embedding` column is once again reset to `null` after updating the title. This is because the trigger we added to clear existing embeddings fires when either the `content` or `title` columns are updated. The embedding will be regenerated by the Edge Function in the next scheduled task.

Wait up to 10 seconds for the next task to run, then check the `embedding` column again:

```
123select id, embeddingfrom documentswhere title = 'Understanding Vector Databases with Supabase';
```

You should see the updated embedding for the document.

## Troubleshooting[#](#troubleshooting)

The `embed` Edge Function processes a batch of embedding jobs and returns a `200 OK` response with a list of completed and failed jobs in the body. For example:

```
1234567891011121314151617181920212223{  "completedJobs": [    {      "jobId": "1",      "id": "1",      "schema": "public",      "table": "documents",      "contentFunction": "embedding_input",      "embeddingColumn": "embedding"    }  ],  "failedJobs": [    {      "jobId": "2",      "id": "2",      "schema": "public",      "table": "documents",      "contentFunction": "embedding_input",      "embeddingColumn": "embedding",      "error": "error connecting to openai api"    }  ]}
```

It also returns the number of completed and failed jobs in the response headers. For example:

```
12x-completed-jobs: 1x-failed-jobs: 1
```

You can also use the `x-deno-execution-id` header to trace the execution of the Edge Function within the [dashboard](https://supabase.com/dashboard/project/_/functions) logs.

Each failed job includes an `error` field with a description of the failure. Reasons for a job failing could include:

-   An error generating the embedding via external API
-   An error connecting to the database
-   The edge function being terminated (e.g. due to a wall clock limit)
-   Any other error thrown during processing

`pg_net` stores HTTP responses in the `net._http_response` table, which can be queried to diagnose issues with the embedding generation process.

```
123456select  *from  net._http_responsewhere  (headers->>'x-failed-jobs')::int > 0;
```

## Conclusion[#](#conclusion)

Automating embedding generation and updates in Postgres allow you to build powerful semantic search capabilities without the complexity of managing embeddings manually.

By combining Postgres features like triggers, queues, and other extensions with Supabase Edge Functions, we can create a robust system that handles embedding generation asynchronously and retries failed jobs automatically.

This system can be customized to work with any content and embedding generation service, providing a flexible and scalable solution for semantic search in Postgres.

## See also[#](#see-also)

-   [What are embeddings?](https://supabase.com/docs/guides/ai/concepts)
-   [Semantic search](https://supabase.com/docs/guides/ai/semantic-search)
-   [Vector indexes](https://supabase.com/docs/guides/ai/vector-indexes)
-   [Supabase Edge Functions](https://supabase.com/docs/guides/functions)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/automatic-embeddings.mdx)

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