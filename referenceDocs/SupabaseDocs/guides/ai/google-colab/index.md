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

5.  [Google Colab](https://supabase.com/docs/guides/ai/google-colab)

# 

Google Colab

## 

Use Google Colab to manage your Supabase Vector store.

* * *

[![](https://supabase.com/docs/img/ai/colab-badge.svg)](https://colab.research.google.com/github/supabase/supabase/blob/master/examples/ai/vector_hello_world.ipynb)

Google Colab is a hosted Jupyter Notebook service. It provides free access to computing resources, including GPUs and TPUs, and is well-suited to machine learning, data science, and education. We can use Colab to manage collections using [Supabase Vecs](https://supabase.com/docs/guides/ai/vecs-python-client).

In this tutorial we'll connect to a database running on the Supabase [platform](https://supabase.com/dashboard/). If you don't already have a database, you can create one here: [database.new](https://database.new).

## Create a new notebook[#](#create-a-new-notebook)

Start by visiting [colab.research.google.com](https://colab.research.google.com/). There you can create a new notebook.

![Google Colab new notebook](https://supabase.com/docs/img/ai/google-colab/colab-new.png)

## Install Vecs[#](#install-vecs)

We'll use the Supabase Vector client, [Vecs](https://supabase.com/docs/guides/ai/vecs-python-client), to manage our collections.

At the top of the notebook add the notebook paste the following code and hit the "execute" button (`ctrl+enter`):

```
1pip install vecs
```

![Install vecs](https://supabase.com/docs/img/ai/google-colab/install-vecs.png)

## Connect to your database[#](#connect-to-your-database)

Find the Postgres pooler connection string for your Supabase project in the [database settings](https://supabase.com/dashboard/project/_/settings/database) of the dashboard. Copy the "URI" format, which should look something like `postgres://postgres.xxxx:password@xxxx.pooler.supabase.com:6543/postgres`

Create a new code block below the install block (`ctrl+m b`) and add the following code using the Postgres URI you copied above:

```
123456import vecsDB_CONNECTION = "postgres://postgres.xxxx:password@xxxx.pooler.supabase.com:6543/postgres"# create vector store clientvx = vecs.create_client(DB_CONNECTION)
```

Execute the code block (`ctrl+enter`). If no errors were returned then your connection was successful.

## Create a collection[#](#create-a-collection)

Now we're going to create a new collection and insert some documents.

Create a new code block below the install block (`ctrl+m b`). Add the following code to the code block and execute it (`ctrl+enter`):

```
12345678910111213141516collection = vx.get_or_create_collection(name="colab_collection", dimension=3)collection.upsert(    vectors=[        (         "vec0",           # the vector's identifier         [0.1, 0.2, 0.3],  # the vector. list or np.array         {"year": 1973}    # associated  metadata        ),        (         "vec1",         [0.7, 0.8, 0.9],         {"year": 2012}        )    ])
```

This will create a table inside your database within the `vecs` schema, called `colab_collection`. You can view the inserted items in the [Table Editor](https://supabase.com/dashboard/project/_/editor/), by selecting the `vecs` schema from the schema dropdown.

![Colab documents](https://supabase.com/docs/img/ai/google-colab/colab-documents.png)

## Query your documents[#](#query-your-documents)

Now we can search for documents based on their similarity. Create a new code block and execute the following code:

```
12345678collection.query(    query_vector=[0.4,0.5,0.6],  # required    limit=5,                     # number of records to return    filters={},                  # metadata filters    measure="cosine_distance",   # distance measure to use    include_value=False,         # should distance measure values be returned?    include_metadata=False,      # should record metadata be returned?)
```

You will see that this returns two documents in an array `['vec1', 'vec0']`:

![Colab results](https://supabase.com/docs/img/ai/google-colab/colab-results.png)

It also returns a warning:

```
1Query does not have a covering index for cosine_distance.
```

You can lean more about creating indexes in the [Vecs documentation](https://supabase.github.io/vecs/api/#create-an-index).

## Resources[#](#resources)

-   Vecs API: [supabase.github.io/vecs/api](https://supabase.github.io/vecs/api)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/google-colab.mdx)

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