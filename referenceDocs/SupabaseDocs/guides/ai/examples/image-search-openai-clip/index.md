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

3.  Python Examples

5.  [Image search with OpenAI CLIP](https://supabase.com/docs/guides/ai/examples/image-search-openai-clip)

# 

Image Search with OpenAI CLIP

## 

Implement image search with the OpenAI CLIP Model and Supabase Vector.

* * *

The [OpenAI CLIP Model](https://github.com/openai/CLIP) was trained on a variety of (image, text)-pairs. You can use the CLIP model for:

-   Text-to-Image / Image-To-Text / Image-to-Image / Text-to-Text Search
-   You can fine-tune it on your own image and text data with the regular `SentenceTransformers` training code.

[`SentenceTransformers`](https://www.sbert.net/examples/applications/image-search/README.html) provides models that allow you to embed images and text into the same vector space. You can use this to find similar images as well as to implement image search.

You can find the full application code as a Python Poetry project on [GitHub](https://github.com/supabase/supabase/tree/master/examples/ai/image_search#image-search-with-supabase-vector).

## Create a new Python project with Poetry[#](#create-a-new-python-project-with-poetry)

[Poetry](https://python-poetry.org/) provides packaging and dependency management for Python. If you haven't already, install poetry via pip:

```
1pip install poetry
```

Then initialize a new project:

```
1poetry new image-search
```

## Setup Supabase project[#](#setup-supabase-project)

If you haven't already, [install the Supabase CLI](https://supabase.com/docs/guides/cli), then initialize Supabase in the root of your newly created poetry project:

```
1supabase init
```

Next, start your local Supabase stack:

```
1supabase start
```

This will start up the Supabase stack locally and print out a bunch of environment details, including your local `DB URL`. Make a note of that for later user.

## Install the dependencies[#](#install-the-dependencies)

We will need to add the following dependencies to our project:

-   [`vecs`](https://github.com/supabase/vecs#vecs): Supabase Vector Python Client.
-   [`sentence-transformers`](https://huggingface.co/sentence-transformers/clip-ViT-B-32): a framework for sentence, text and image embeddings (used with OpenAI CLIP model)
-   [`matplotlib`](https://matplotlib.org/): for displaying our image result

```
1poetry add vecs sentence-transformers matplotlib
```

## Import the necessary dependencies[#](#import-the-necessary-dependencies)

At the top of your main python script, import the dependencies and store your `DB URL` from above in a variable:

```
1234567from PIL import Imagefrom sentence_transformers import SentenceTransformerimport vecsfrom matplotlib import pyplot as pltfrom matplotlib import image as mpimgDB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"
```

## Create embeddings for your images[#](#create-embeddings-for-your-images)

In the root of your project, create a new folder called `images` and add some images. You can use the images from the example project on [GitHub](https://github.com/supabase/supabase/tree/master/examples/ai/image_search/images) or you can find license free images on [Unsplash](https://unsplash.com).

Next, create a `seed` method, which will create a new Supabase Vector Collection, generate embeddings for your images, and upsert the embeddings into your database:

```
12345678910111213141516171819202122232425262728293031323334353637383940414243def seed():    # create vector store client    vx = vecs.create_client(DB_CONNECTION)    # create a collection of vectors with 3 dimensions    images = vx.get_or_create_collection(name="image_vectors", dimension=512)    # Load CLIP model    model = SentenceTransformer('clip-ViT-B-32')    # Encode an image:    img_emb1 = model.encode(Image.open('./images/one.jpg'))    img_emb2 = model.encode(Image.open('./images/two.jpg'))    img_emb3 = model.encode(Image.open('./images/three.jpg'))    img_emb4 = model.encode(Image.open('./images/four.jpg'))    # add records to the *images* collection    images.upsert(        records=[            (                "one.jpg",        # the vector's identifier                img_emb1,          # the vector. list or np.array                {"type": "jpg"}   # associated  metadata            ), (                "two.jpg",                img_emb2,                {"type": "jpg"}            ), (                "three.jpg",                img_emb3,                {"type": "jpg"}            ), (                "four.jpg",                img_emb4,                {"type": "jpg"}            )        ]    )    print("Inserted images")    # index the collection for fast search performance    images.create_index()    print("Created index")
```

Add this method as a script in your `pyproject.toml` file:

```
123[tool.poetry.scripts]seed = "image_search.main:seed"search = "image_search.main:search"
```

After activating the virtual environment with `poetry shell` you can now run your seed script via `poetry run seed`. You can inspect the generated embeddings in your local database by visiting the local Supabase dashboard at [localhost:54323](http://localhost:54323/project/default/editor), selecting the `vecs` schema, and the `image_vectors` database.

## Perform an image search from a text query[#](#perform-an-image-search-from-a-text-query)

With Supabase Vector we can query our embeddings. We can use either an image as search input or alternative we can generate an embedding from a string input and use that as the query input:

```
1234567891011121314151617181920212223def search():    # create vector store client    vx = vecs.create_client(DB_CONNECTION)    images = vx.get_or_create_collection(name="image_vectors", dimension=512)    # Load CLIP model    model = SentenceTransformer('clip-ViT-B-32')    # Encode text query    query_string = "a bike in front of a red brick wall"    text_emb = model.encode(query_string)    # query the collection filtering metadata for "type" = "jpg"    results = images.query(        data=text_emb,                      # required        limit=1,                            # number of records to return        filters={"type": {"$eq": "jpg"}},   # metadata filters    )    result = results[0]    print(result)    plt.title(result)    image = mpimg.imread('./images/' + result)    plt.imshow(image)    plt.show()
```

By limiting the query to one result, we can show the most relevant image to the user. Finally we use `matplotlib` to show the image result to the user.

Go ahead and test it out by running `poetry run search` and you will be presented with an image of a "bike in front of a red brick wall".

## Conclusion[#](#conclusion)

With just a couple of lines of Python you are able to implement image search as well as reverse image search using OpenAI's CLIP model and Supabase Vector.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/examples/image-search-openai-clip.mdx)

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