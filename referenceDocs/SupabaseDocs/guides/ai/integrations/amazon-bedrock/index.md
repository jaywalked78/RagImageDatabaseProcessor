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

5.  [Amazon Bedrock](https://supabase.com/docs/guides/ai/integrations/amazon-bedrock)

# 

Amazon Bedrock

* * *

[Amazon Bedrock](https://aws.amazon.com/bedrock) is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Mistral AI, Stability AI, and Amazon. Each model is accessible through a common API which implements a broad set of features to help build generative AI applications with security, privacy, and responsible AI in mind.

This guide will walk you through an example using Amazon Bedrock SDK with `vecs`. We will create embeddings using the Amazon Titan Embeddings G1 – Text v1.2 (amazon.titan-embed-text-v1) model, insert these embeddings into a Postgres database using vecs, and then query the collection to find the most similar sentences to a given query sentence.

## Create an environment[#](#create-an-environment)

First, you need to set up your environment. You will need Python 3.7+ with the `vecs` and `boto3` libraries installed.

You can install the necessary Python libraries using pip:

```
1pip install vecs boto3
```

You'll also need:

-   [Credentials to your AWS account](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
-   [A Postgres Database with the pgvector extension](https://supabase.com/docs/guides/ai/integrations/hosting.md)

## Create embeddings[#](#create-embeddings)

Next, we will use Amazon’s Titan Embedding G1 - Text v1.2 model to create embeddings for a set of sentences.

```
12345678910111213141516171819202122232425262728293031323334import boto3import vecsimport jsonclient = boto3.client(    'bedrock-runtime',    region_name='us-east-1',	# Credentials from your AWS account    aws_access_key_id='<replace_your_own_credentials>',    aws_secret_access_key='<replace_your_own_credentials>',    aws_session_token='<replace_your_own_credentials>',)dataset = [    "The cat sat on the mat.",    "The quick brown fox jumps over the lazy dog.",    "Friends, Romans, countrymen, lend me your ears",    "To be or not to be, that is the question.",]embeddings = []for sentence in dataset:    # invoke the embeddings model for each sentence    response = client.invoke_model(        body= json.dumps({"inputText": sentence}),        modelId= "amazon.titan-embed-text-v1",        accept = "application/json",        contentType = "application/json"    )    # collect the embedding from the response    response_body = json.loads(response["body"].read())    # add the embedding to the embedding list    embeddings.append((sentence, response_body.get("embedding"), {}))
```

### Store the embeddings with vecs[#](#store-the-embeddings-with-vecs)

Now that we have our embeddings, we can insert them into a Postgres database using vecs.

```
12345678910111213141516import vecsDB_CONNECTION = "postgresql://<user>:<password>@<host>:<port>/<db_name>"# create vector store clientvx = vecs.Client(DB_CONNECTION)# create a collection named 'sentences' with 1536 dimensional vectors# to match the default dimension of the Titan Embeddings G1 - Text modelsentences = vx.get_or_create_collection(name="sentences", dimension=1536)# upsert the embeddings into the 'sentences' collectionsentences.upsert(records=embeddings)# create an index for the 'sentences' collectionsentences.create_index()
```

### Querying for most similar sentences[#](#querying-for-most-similar-sentences)

Now, we query the `sentences` collection to find the most similar sentences to a sample query sentence. First need to create an embedding for the query sentence. Next, we query the collection we created earlier to find the most similar sentences.

```
123456789101112131415161718192021222324252627query_sentence = "A quick animal jumps over a lazy one."# create vector store clientvx = vecs.Client(DB_CONNECTION)# create an embedding for the query sentenceresponse = client.invoke_model(        body= json.dumps({"inputText": query_sentence}),        modelId= "amazon.titan-embed-text-v1",        accept = "application/json",        contentType = "application/json"    )response_body = json.loads(response["body"].read())query_embedding = response_body.get("embedding")# query the 'sentences' collection for the most similar sentencesresults = sentences.query(    data=query_embedding,    limit=3,    include_value = True)# print the resultsfor result in results:    print(result)
```

This returns the most similar 3 records and their distance to the query vector.

```
123('The quick brown fox jumps over the lazy dog.', 0.27600620558852)('The cat sat on the mat.', 0.609986272479202)('To be or not to be, that is the question.', 0.744849503688346)
```

## Resources[#](#resources)

-   [Amazon Bedrock](https://aws.amazon.com/bedrock)
-   [Amazon Titan](https://aws.amazon.com/bedrock/titan)
-   [Semantic Image Search with Amazon Titan](https://supabase.com/docs/guides/ai/examples/semantic-image-search-amazon-titan)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/integrations/amazon-bedrock.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FA3uND5sgiO0%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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