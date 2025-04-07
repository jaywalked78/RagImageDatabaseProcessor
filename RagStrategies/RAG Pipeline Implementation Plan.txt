RAG Pipeline Implementation Plan

Ingestion Pipeline Steps

    Initialize Clients & Config:

        Load environment variables: AIRTABLE_PAT, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, FRAME_BASE_DIR, SUPABASE_URL, SUPABASE_KEY, VOYAGE_API_KEY.

        Initialize clients: Airtable, Supabase, Voyager 3, potentially an LLM client.

        Define target Supabase table schema conceptually:

              
        CREATE TABLE frame_chunks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            airtable_record_id TEXT NOT NULL,
            frame_path TEXT NOT NULL,
            chunk_sequence_id INT NOT NULL,
            chunk_text TEXT,
            full_metadata JSONB,
            embedding VECTOR(1024), -- Or Voyager 3's dimension
            created_at TIMESTAMPTZ DEFAULT now()
        );
        -- Indexes
        CREATE INDEX idx_airtable_record_id ON frame_chunks (airtable_record_id);
        CREATE INDEX idx_embedding ON frame_chunks USING hnsw (embedding vector_cosine_ops)
          WITH (m = 16, ef_construction = 64);
        CREATE INDEX idx_full_metadata ON frame_chunks USING gin (full_metadata jsonb_path_ops);

            

        IGNORE_WHEN_COPYING_START

    Use code with caution.SQL
    IGNORE_WHEN_COPYING_END

Fetch Data from Airtable ([N8N_FETCH_AIRTABLE_DATA]):

    Use Airtable client and PAT to fetch records.

    Iterate through records, each containing metadata and frame reference.

    Conceptual Python:

          
    import os
    from pyairtable import Api

    airtable_api = Api(os.getenv("AIRTABLE_PAT"))
    table = airtable_api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_NAME"))
    all_records = table.all()

    for record in all_records:
        process_airtable_record(record)

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Locate and Load Frame Data:

    Construct full frame file path using FRAME_BASE_DIR and record reference.

    Load frame data (handle different types like image/video). Handle errors.

    Conceptual Python:

          
    import os
    from pathlib import Path
    # from frame_utils import frame_loader

    def process_airtable_record(record):
        frame_ref = record['fields'].get('frame_filename')
        metadata = record['fields']
        airtable_id = record['id']
        if not frame_ref: return

        base_dir = os.getenv("FRAME_BASE_DIR")
        frame_path = Path(base_dir) / frame_ref
        relative_path = frame_ref
        if not frame_path.exists(): return

        try:
            # frame_data = frame_loader(frame_path)
            frame_data = f"Content of {frame_path}" # Placeholder
            structure_and_chunk(frame_data, metadata, airtable_id, relative_path)
        except Exception as e: print(f"Error: {e}")

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Structure Metadata & Generate Frame Description (Ref #6, #12, #8):

    Use an LLM (possibly multimodal) to generate a textual description of frame_data, analyze raw metadata from Airtable, structure/clean/enhance metadata, and add source tracking info.

    Output a consistent JSON object (structured_metadata).

    Conceptual Python:

          
    # from llm_utils import llm_client

    def structure_and_chunk(frame_data, raw_metadata, airtable_id, frame_path_rel):
        prompt = f"""Analyze frame data and raw metadata...
        Frame Description: [Generate description]
        Raw Metadata: {raw_metadata}
        Structure into JSON including: frame_summary, cleaned fields, source_airtable_id: '{airtable_id}', source_frame_path: '{frame_path_rel}', classification_tags. Output ONLY JSON.
        """
        # structured_metadata_json = llm_client.generate(prompt)
        structured_metadata = {"frame_summary": "Summary...", "timestamp": ..., "tags": ..., "source_airtable_id": airtable_id, "source_frame_path": frame_path_rel, "classification_tags": ["tag1"]} # Example
        chunk_content(structured_metadata)

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Generate Text for Chunking & Embedding (Ref #40):

    Create a single text representation from structured_metadata, including key fields for semantic meaning, using a clear format.

    Conceptual Python:

          
    def create_text_representation(metadata_json):
        text = f"Frame Summary: {metadata_json.get('frame_summary', '')}\\n"
        text += f"Tags: {', '.join(metadata_json.get('tags', []))}\\n"
        text += f"Timestamp: {metadata_json.get('timestamp', '')}\\n"
        # Add other key metadata selectively (Ref #35)
        return text

    def chunk_content(structured_metadata):
         text_to_chunk = create_text_representation(structured_metadata)
         perform_semantic_chunking(text_to_chunk, structured_metadata)

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Perform Semantic Chunking (Ref #30) with Overlap (Ref #41):

    Apply semantic chunking (e.g., using SemanticTextSplitter based on embedding similarity) to the text_to_chunk.

    Configure appropriate chunk_overlap.

    Yields one or more text chunk strings.

    Conceptual Python:

          
    # from langchain_experimental.text_splitter import SemanticChunker
    # from langchain_openai import OpenAIEmbeddings # Or Voyager 3

    def perform_semantic_chunking(text_to_chunk, structured_metadata):
        # text_splitter = SemanticChunker(...)
        # chunks = text_splitter.split_text(text_to_chunk)
        # Fallback simple splitter:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text_to_chunk)
        for i, chunk_text in enumerate(chunks):
             embed_and_store(chunk_text, i, structured_metadata)

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Embed Chunk using Voyager 3 (Multimodal):

    For each chunk_text, prepare input for Voyager 3 (text only or text + frame_data, per Voyager 3 docs).

    Call the Voyager 3 embedding model.

    Conceptual Python:

          
    # from voyager_client import VoyagerEmbedder
    # voyager_embedder = VoyagerEmbedder(...)

    def embed_and_store(chunk_text, chunk_seq_id, structured_metadata):
        # embedding_input = chunk_text # OR {"text": chunk_text, "image": frame_data}
        # embedding = voyager_embedder.embed(embedding_input, model="voyager-3-multimodal")
        embedding = [0.1] * 1024 # Placeholder
        store_in_supabase(chunk_text, chunk_seq_id, structured_metadata, embedding)

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Store in Supabase:

    For each chunk and embedding, construct the record for the frame_chunks table (including chunk_text, full_metadata JSONB, embedding, source IDs, sequence ID).

    Use Supabase client to insert the record (consider batching).

    Conceptual Python:

          
    # from supabase_py import create_client, Client
    # supabase: Client = create_client(...)

    def store_in_supabase(chunk_text, chunk_seq_id, structured_metadata, embedding):
        data_to_insert = {
            "airtable_record_id": structured_metadata["source_airtable_id"],
            "frame_path": structured_metadata["source_frame_path"],
            "chunk_sequence_id": chunk_seq_id,
            "chunk_text": chunk_text,
            "full_metadata": structured_metadata,
            "embedding": embedding,
        }
        try:
            # response = supabase.table("frame_chunks").insert(data_to_insert).execute()
            print(f"Stored chunk {chunk_seq_id} for {structured_metadata['source_airtable_id']}")
        except Exception as e: print(f"Error storing chunk: {e}")

    # [N8N_PROCESS_CHUNK_VIA_WEBHOOK] Optional webhook trigger point

        

    IGNORE_WHEN_COPYING_START

        Use code with caution.Python
        IGNORE_WHEN_COPYING_END

Retrieval Strategy Steps

    Receive User Query: Get query string from chatbot interface.

          
    user_query = "Show me frames tagged 'outdoor' from last week showing a red car."

        

    IGNORE_WHEN_COPYING_START

Use code with caution.Python
IGNORE_WHEN_COPYING_END

Query Expansion (Ref #15): Use LLM to generate diverse variations of the user query.

      
# expansion_prompt = f"Generate 3 diverse variations..."
# query_variations = eval(llm_client.generate(expansion_prompt))
query_variations = ["variation 1", "variation 2", "variation 3"] # Placeholder
all_queries = [user_query] + query_variations

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Self-Querying / Metadata Inference (for Original Query) (Ref #4): Use LLM (with tool use/function calling) to parse original query, extracting semantic query text and structured metadata filters based on defined schema.

      
# self_query_prompt = f"Parse query '{user_query}' for semantic part and filters..."
# llm_response = llm_client_tool_use.generate(...)
# semantic_query_text = tool_call.arguments.get(...)
# inferred_filters = tool_call.arguments.get(...) # e.g., {'tags': ['outdoor'], ...}

semantic_query_text = "outdoor red car" # Placeholder
inferred_filters = {"tags": ["outdoor"], "min_timestamp": "2024-..."} # Placeholder

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Embed Queries: Embed the semantic_query_text and all query_variations using Voyager 3 (text mode).

      
# original_query_embedding = voyager_embedder.embed(semantic_query_text, ...)
# variation_embeddings = [voyager_embedder.embed(q, ...) for q in query_variations]
# all_query_embeddings = [original_query_embedding] + variation_embeddings

original_query_embedding = [0.2] * 1024 # Placeholder
variation_embeddings = [[0.3]*1024, [0.4]*1024, [0.5]*1024] # Placeholders
all_query_embeddings = [original_query_embedding] + variation_embeddings

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Construct & Execute Supabase Hybrid Queries (Ref #32, #26):

    Define initial_k (e.g., 20).

    For each query embedding: construct Supabase query. Apply inferred_filters (WHERE clause on full_metadata) only to the original query's search. Include ORDER BY embedding <=> query_vector LIMIT initial_k. Select id, chunk_text, full_metadata, distance. Execute queries.

    Conceptual Python:

          
    # supabase: Client = create_client(...)
    initial_k = 20
    all_results = []
    for i, query_embedding in enumerate(all_query_embeddings):
        query_filters = inferred_filters if i == 0 else {}
        try:
            # response = supabase.rpc('hybrid_search', {'query_embedding': ..., 'query_filters': ..., 'match_limit': initial_k}).execute()
            # results = response.data
            # FAKE results:
            results = [{'id': f'id_{i}_{j}', 'chunk_text': f'Chunk {i}-{j}', 'full_metadata': {}, 'distance': 0.1*(i+1)+0.01*j} for j in range(initial_k)]
            all_results.append(results)
        except Exception as e: print(f"Error query {i}: {e}"); all_results.append([])

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Python
    IGNORE_WHEN_COPYING_END

Result Fusion (Ref #15 - RRF): Aggregate results and apply Reciprocal Rank Fusion (RRF) based on ranks/scores from each query list.

      
def reciprocal_rank_fusion(results_lists, k=60):
    fused_scores = {}
    for results in results_lists:
        for rank, doc in enumerate(results):
            doc_id = doc['id']; fused_scores.setdefault(doc_id, 0); fused_scores[doc_id] += 1 / (k + rank)
    reranked_results = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
    fused_docs_map = {doc['id']: doc for results in results_lists for doc in results}
    final_fused_list = [fused_docs_map[doc_id] for doc_id, score in reranked_results if doc_id in fused_docs_map]
    return final_fused_list

fused_results = reciprocal_rank_fusion(all_results)

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Post-Retrieval Reranking (Ref #9): Take top M fused results (e.g., M=20) and pass (user_query, chunk_text) pairs to a dedicated reranker model. Sort results by reranker score.

      
# from reranker_client import Reranker
# reranker = Reranker()
rerank_candidates_count = 20
candidates_for_reranking = fused_results[:rerank_candidates_count]
# rerank_inputs = [(user_query, candidate['chunk_text']) for candidate in candidates_for_reranking]
# reranked_scores = reranker.rank(rerank_inputs)
# Add scores back and sort...
# FAKE RERANKING:
reranked_finalists = candidates_for_reranking

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Context Assembly & Formatting (Ref #31, #40): Select final top P chunks (e.g., P=5) from reranked list. Optionally apply Long-Context Reordering. Format chunks and relevant metadata (source info Ref #37) into a structured context block for the LLM.

      
final_context_count = 5
final_chunks = reranked_finalists[:final_context_count]
# Optional Long-Context Reordering...
context_for_llm = ""
for i, chunk in enumerate(final_chunks):
    context_for_llm += f"--- Context {i+1} ---\\n"
    context_for_llm += f"Source Path: {chunk['full_metadata'].get('source_frame_path', 'N/A')}\\n"
    context_for_llm += f"Airtable ID: {chunk['full_metadata'].get('source_airtable_id', 'N/A')}\\n"
    context_for_llm += f"Content: {chunk['chunk_text']}\\n\\n"

# [N8N_SEND_QUERY_RESULT] Send context/results to n8n

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

LLM Generation: Pass user query and assembled context to the chat LLM. Instruct it to answer based only on context and cite sources. Return the LLM response.

      
# from chat_llm_client import ChatLLM
# chat_llm = ChatLLM()
generation_prompt = f"""Based ONLY on the following context, answer the user's query. Cite sources...
User Query: {user_query}
Context:
{context_for_llm}
Answer:
"""
# final_answer = chat_llm.generate(generation_prompt)
final_answer = "According to frame path/xyz (Airtable ID: rec123)..." # Placeholder
# Send final_answer to chatbot UI

    