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

3.  Third-Party Tools

5.  [LlamaIndex](https://supabase.com/docs/guides/ai/integrations/llamaindex)

# 

Learn how to integrate Supabase with LlamaIndex, a data framework for your LLM applications.

## 

Learn how to integrate Supabase with LlamaIndex, a data framework for your LLM applications.

* * *

This guide will walk you through a basic example using the LlamaIndex [`SupabaseVectorStore`](https://github.com/supabase/supabase/blob/master/examples/ai/llamaindex/llamaindex.ipynb).

## Project setup[#](#project-setup)

Let's create a new Postgres database. This is as simple as starting a new Project in Supabase:

1.  [Create a new project](https://database.new/) in the Supabase dashboard.
2.  Enter your project details. Remember to store your password somewhere safe.

Your database will be available in less than a minute.

**Finding your credentials:**

You can find your project credentials inside the project [settings](https://supabase.com/dashboard/project/_/settings/), including:

-   [Database credentials](https://supabase.com/dashboard/project/_/settings/database): connection strings and connection pooler details.
-   [API credentials](https://supabase.com/dashboard/project/_/settings/database): your serverless API URL and `anon` / `service_role` keys.

## Launching a notebook[#](#launching-a-notebook)

Launch our [LlamaIndex](https://github.com/supabase/supabase/blob/master/examples/ai/llamaindex/llamaindex.ipynb) notebook in Colab:

[![](https://supabase.com/docs/img/ai/colab-badge.svg)](https://colab.research.google.com/github/supabase/supabase/blob/master/examples/ai/llamaindex/llamaindex.ipynb)

At the top of the notebook, you'll see a button `Copy to Drive`. Click this button to copy the notebook to your Google Drive.

## Fill in your OpenAI credentials[#](#fill-in-your-openai-credentials)

Inside the Notebook, add your `OPENAI_API_KEY` key. Find the cell which contains this code:

```
12import osos.environ['OPENAI_API_KEY'] = "[your_openai_api_key]"
```

## Connecting to your database[#](#connecting-to-your-database)

Inside the Notebook, find the cell which specifies the `DB_CONNECTION`. It will contain some code like this:

```
1234DB_CONNECTION = "postgresql://<user>:<password>@<host>:<port>/<db_name>"# create vector store clientvx = vecs.create_client(DB_CONNECTION)
```

Replace the `DB_CONNECTION` with your own connection string for your database. You can find the Postgres connection string in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database) of your Supabase project.

SQLAlchemy requires the connection string to start with `postgresql://` (instead of `postgres://`). Don't forget to rename this after copying the string from the dashboard.

You must use the "connection pooling" string (domain ending in `*.pooler.supabase.com`) with Google Colab since Colab does not support IPv6.

## Stepping through the notebook[#](#stepping-through-the-notebook)

Now all that's left is to step through the notebook. You can do this by clicking the "execute" button (`ctrl+enter`) at the top left of each code cell. The notebook guides you through the process of creating a collection, adding data to it, and querying it.

You can view the inserted items in the [Table Editor](https://supabase.com/dashboard/project/_/editor/), by selecting the `vecs` schema from the schema dropdown.

![Colab documents](https://supabase.com/docs/img/ai/google-colab/colab-documents.png)

## Resources[#](#resources)

-   Visit the LlamaIndex + `SupabaseVectorStore` [docs](https://gpt-index.readthedocs.io/en/latest/examples/vector_stores/SupabaseVectorIndexDemo.html)
-   Visit the official LlamaIndex [repo](https://github.com/jerryjliu/llama_index/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/integrations/llamaindex.mdx)

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