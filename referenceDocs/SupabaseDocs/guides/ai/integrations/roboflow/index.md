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

5.  [Roboflow](https://supabase.com/docs/guides/ai/integrations/roboflow)

# 

Roboflow

## 

Learn how to integrate Supabase with Roboflow, a tool for running fine-tuned and foundation vision models.

* * *

In this guide, we will walk through two examples of using [Roboflow Inference](https://inference.roboflow.com) to run fine-tuned and foundation models. We will run inference and save predictions using an object detection model and [CLIP](https://github.com/openai/CLIP).

## Project setup[#](#project-setup)

Let's create a new Postgres database. This is as simple as starting a new Project in Supabase:

1.  [Create a new project](https://database.new/) in the Supabase dashboard.
2.  Enter your project details. Remember to store your password somewhere safe.

Your database will be available in less than a minute.

**Finding your credentials:**

You can find your project credentials inside the project [settings](https://supabase.com/dashboard/project/_/settings/), including:

-   [Database credentials](https://supabase.com/dashboard/project/_/settings/database): connection strings and connection pooler details.
-   [API credentials](https://supabase.com/dashboard/project/_/settings/database): your serverless API URL and `anon` / `service_role` keys.

## Save computer vision predictions[#](#save-computer-vision-predictions)

Once you have a trained vision model, you need to create business logic for your application. In many cases, you want to save inference results to a file.

The steps below show you how to run a vision model locally and save predictions to Supabase.

### Preparation: Set up a model[#](#preparation-set-up-a-model)

Before you begin, you will need an object detection model trained on your data.

You can [train a model on Roboflow](https://blog.roboflow.com/getting-started-with-roboflow/), leveraging end-to-end tools from data management and annotation to deployment, or [upload custom model weights](https://docs.roboflow.com/deploy/upload-custom-weights) for deployment.

All models have an infinitely scalable API through which you can query your model, and can be run locally.

For this guide, we will use a demo [rock, paper, scissors](https://universe.roboflow.com/roboflow-58fyf/rock-paper-scissors-sxsw) model.

### Step 1: Install and start Roboflow Inference[#](#step-1-install-and-start-roboflow-inference)

You will deploy our model locally using Roboflow Inference, a computer vision inference server.

To install and start Roboflow Inference, first install Docker on your machine.

Then, run:

```
1pip install inference inference-cli inference-sdk && inference server start
```

An inference server will be available at `http://localhost:9001`.

### Step 2: Run inference on an image[#](#step-2-run-inference-on-an-image)

You can run inference on images and videos. Let's run inference on an image.

Create a new Python file and add the following code:

```
12345678910111213from inference_sdk import InferenceHTTPClientimage = "example.jpg"MODEL_ID = "rock-paper-scissors-sxsw/11"client = InferenceHTTPClient(    api_url="http://localhost:9001",    api_key="ROBOFLOW_API_KEY")with client.use_model(MODEL_ID):    predictions = client.infer(image)print(predictions)
```

Above, replace:

1.  The image URL with the name of the image on which you want to run inference.
2.  `ROBOFLOW_API_KEY` with your Roboflow API key. [Learn how to retrieve your Roboflow API key](https://docs.roboflow.com/api-reference/authentication#retrieve-an-api-key).
3.  `MODEL_ID` with your Roboflow model ID. [Learn how to retrieve your model ID](https://docs.roboflow.com/api-reference/workspace-and-project-ids).

When you run the code above, a list of predictions will be printed to the console:

```
1{'time': 0.05402109300121083, 'image': {'width': 640, 'height': 480}, 'predictions': [{'x': 312.5, 'y': 392.0, 'width': 255.0, 'height': 110.0, 'confidence': 0.8620790839195251, 'class': 'Paper', 'class_id': 0}]}
```

### Step 3: Save results in Supabase[#](#step-3-save-results-in-supabase)

To save results in Supabase, add the following code to your script:

```
12345678910import osfrom supabase import create_client, Clienturl: str = os.environ.get("SUPABASE_URL")key: str = os.environ.get("SUPABASE_KEY")supabase: Client = create_client(url, key)result = supabase.table('predictions') \    .insert({"filename": image, "predictions": predictions}) \    .execute()
```

You can then query your predictions using the following code:

```
123456result = supabase.table('predictions') \    .select("predictions") \    .filter("filename", "eq", image) \    .execute()print(result)
```

Here is an example result:

```
1data=[{'predictions': {'time': 0.08492901099998562, 'image': {'width': 640, 'height': 480}, 'predictions': [{'x': 312.5, 'y': 392.0, 'width': 255.0, 'height': 110.0, 'confidence': 0.8620790839195251, 'class': 'Paper', 'class_id': 0}]}}, {'predictions': {'time': 0.08818970100037404, 'image': {'width': 640, 'height': 480}, 'predictions': [{'x': 312.5, 'y': 392.0, 'width': 255.0, 'height': 110.0, 'confidence': 0.8620790839195251, 'class': 'Paper', 'class_id': 0}]}}] count=None
```

## Calculate and save CLIP embeddings[#](#calculate-and-save-clip-embeddings)

You can use the Supabase vector database functionality to store and query CLIP embeddings.

Roboflow Inference provides a HTTP interface through which you can calculate image and text embeddings using CLIP.

### Step 1: Install and start Roboflow Inference[#](#step-1-install-and-start-roboflow-inference)

See [Step #1: Install and Start Roboflow Inference](#step-1-install-and-start-roboflow-inference) above to install and start Roboflow Inference.

### Step 2: Run CLIP on an image[#](#step-2-run-clip-on-an-image)

Create a new Python file and add the following code:

```
1234567891011121314151617181920212223242526272829303132import cv2import supervision as svimport requestsimport base64import osIMAGE_DIR = "images/train/images/"API_KEY = ""SERVER_URL = "http://localhost:9001"results = []for i, image in enumerate(os.listdir(IMAGE_DIR)):    print(f"Processing image {image}")    infer_clip_payload = {        "image": {            "type": "base64",            "value": base64.b64encode(open(IMAGE_DIR + image, "rb").read()).decode("utf-8"),        },    }    res = requests.post(        f"{SERVER_URL}/clip/embed_image?api_key={API_KEY}",        json=infer_clip_payload,    )    embeddings = res.json()['embeddings']    results.append({        "filename": image,        "embeddings": embeddings    })
```

This code will calculate CLIP embeddings for each image in the directory and print the results to the console.

Above, replace:

1.  `IMAGE_DIR` with the directory containing the images on which you want to run inference.
2.  `ROBOFLOW_API_KEY` with your Roboflow API key. [Learn how to retrieve your Roboflow API key](https://docs.roboflow.com/api-reference/authentication#retrieve-an-api-key).

You can also calculate CLIP embeddings in the cloud by setting `SERVER_URL` to `https://infer.roboflow.com`.

### Step 3: Save embeddings in Supabase[#](#step-3-save-embeddings-in-supabase)

You can store your image embeddings in Supabase using the Supabase `vecs` Python package:

First, install `vecs`:

```
1pip install vecs
```

Next, add the following code to your script to create an index:

```
12345678910111213141516171819202122232425import vecsDB_CONNECTION = "postgresql://postgres:[password]@[host]:[port]/[database]"vx = vecs.create_client(DB_CONNECTION)# create a collection of vectors with 3 dimensionsimages = vx.get_or_create_collection(name="image_vectors", dimension=512)for result in results:    image = result["filename"]    embeddings = result["embeddings"][0]    # insert a vector into the collection    images.upsert(        records=[            (                image,                embeddings,                {} # metadata            )        ]    )images.create_index()
```

Replace `DB_CONNECTION` with the authentication information for your database. You can retrieve this from the Supabase dashboard in `Project Settings > Database Settings`.

You can then query your embeddings using the following code:

```
1234567891011121314151617infer_clip_payload = {    "text": "cat",}res = requests.post(    f"{SERVER_URL}/clip/embed_text?api_key={API_KEY}",    json=infer_clip_payload,)embeddings = res.json()['embeddings']result = images.query(    data=embeddings[0],    limit=1)print(result[0])
```

## Resources[#](#resources)

-   [Roboflow Inference documentation](https://inference.roboflow.com)
-   [Roboflow Getting Started guide](https://blog.roboflow.com/getting-started-with-roboflow/)
-   [How to Build a Semantic Image Search Engine with Supabase and OpenAI CLIP](https://blog.roboflow.com/how-to-use-semantic-search-supabase-openai-clip/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/integrations/roboflow.mdx)

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