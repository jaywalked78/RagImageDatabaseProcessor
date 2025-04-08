#!/usr/bin/env python
"""
Database Structure Verification Script

This script connects to the PostgreSQL database and checks:
1. That the database exists and is accessible
2. What schemas and tables contain frame data
3. How many records exist in each table
4. Sample data from each table to verify structure
5. Duplicate frames or chunks that can be cleaned up
"""

import os
import sys
import argparse
import asyncio
import json
import hashlib
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import database connector with proper path
try:
    from src.connectors.postgres_connector import PostgresConnector
except ImportError:
    print("Error: Could not import PostgresConnector.")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

async def check_tables(connector, quiet=False):
    """Check all tables in the database and report on their contents."""
    
    if not quiet:
        print("\n=== Database Structure Check ===\n")
    
    # Get a list of all schemas
    schemas_query = """
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY schema_name;
    """
    
    schemas = await connector.fetch_all(schemas_query)
    if not quiet:
        print(f"Found {len(schemas)} schemas:")
    
    # Store table counts by schema
    schema_tables = {}
    
    for schema in schemas:
        schema_name = schema['schema_name']
        
        # Get all tables in this schema
        tables_query = f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema_name}'
        ORDER BY table_name;
        """
        
        tables = await connector.fetch_all(tables_query)
        schema_tables[schema_name] = [t['table_name'] for t in tables]
        
        if not quiet:
            print(f"\n- Schema: {schema_name}")
            print(f"  Contains {len(tables)} tables:")
        
        for table in tables:
            table_name = table['table_name']
            
            # Get row count
            count_query = f"""
            SELECT COUNT(*) as count FROM "{schema_name}"."{table_name}";
            """
            
            try:
                count_result = await connector.fetch_one(count_query)
                row_count = count_result['count'] if count_result else 0
                
                if not quiet:
                    print(f"  - Table: {table_name} ({row_count} rows)")
                
                # If the table has rows, examine the structure
                if row_count > 0:
                    # Get column information
                    columns_query = f"""
                    SELECT column_name, data_type, character_maximum_length 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                    """
                    
                    columns = await connector.fetch_all(columns_query)
                    if not quiet:
                        print(f"    Columns:")
                        for col in columns:
                            col_type = col['data_type']
                            if col['character_maximum_length']:
                                col_type += f"({col['character_maximum_length']})"
                            print(f"      - {col['column_name']}: {col_type}")
                    
                    # Check if this might be a frame-related table
                    frame_related = any(
                        col['column_name'] in ['frame_path', 'frame_id', 'embedding', 'metadata', 'content'] 
                        for col in columns
                    )
                    
                    if frame_related and not quiet:
                        print(f"    ** Appears to contain frame data **")
                        
                        # Sample data
                        sample_query = f"""
                        SELECT * FROM "{schema_name}"."{table_name}" LIMIT 1;
                        """
                        
                        sample = await connector.fetch_one(sample_query)
                        if sample:
                            print(f"    Sample record:")
                            for key, value in sample.items():
                                # Truncate long values
                                if isinstance(value, (str, list, dict)) and str(value).__len__() > 100:
                                    print(f"      {key}: {str(value)[:100]}... (truncated)")
                                else:
                                    print(f"      {key}: {value}")
            except Exception as e:
                if not quiet:
                    print(f"    Error querying table: {e}")
    
    return schema_tables

async def check_vector_tables(connector, quiet=False):
    """Specifically check for pgvector tables and their contents."""
    
    if not quiet:
        print("\n=== Vector Storage Tables ===\n")
    
    # Check for the pgvector extension
    extension_query = """
    SELECT * FROM pg_extension WHERE extname = 'vector';
    """
    
    extension = await connector.fetch_one(extension_query)
    if not extension:
        if not quiet:
            print("pgvector extension is NOT installed in this database.")
        return {}
    
    if not quiet:
        print("pgvector extension is installed.")
    
    # Find tables with vector columns
    vector_tables_query = """
    SELECT n.nspname as schema, c.relname as table, a.attname as column
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE t.typname = 'vector'
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY n.nspname, c.relname;
    """
    
    vector_tables = await connector.fetch_all(vector_tables_query)
    
    if not vector_tables:
        if not quiet:
            print("No tables with vector columns found.")
        return {}
    
    if not quiet:
        print(f"Found {len(vector_tables)} tables with vector columns:")
    
    vector_table_info = {}
    
    for vt in vector_tables:
        schema_name = vt['schema']
        table_name = vt['table']
        column_name = vt['column']
        
        if not quiet:
            print(f"\n- Table: {schema_name}.{table_name}")
            print(f"  Vector column: {column_name}")
        
        # Get vector dimension
        dim_query = f"""
        SELECT pg_column_size({column_name}) / 4 - 1 as dimension
        FROM "{schema_name}"."{table_name}"
        LIMIT 1;
        """
        
        try:
            dim_result = await connector.fetch_one(dim_query)
            dimension = dim_result['dimension'] if dim_result else None
            
            if dimension and not quiet:
                print(f"  Vector dimension: {dimension}")
            
            # Count records
            count_query = f"""
            SELECT COUNT(*) as count FROM "{schema_name}"."{table_name}";
            """
            
            count_result = await connector.fetch_one(count_query)
            row_count = count_result['count'] if count_result else 0
            
            if not quiet:
                print(f"  Total records: {row_count}")
            
            vector_table_info[f"{schema_name}.{table_name}"] = {
                "schema": schema_name,
                "table": table_name,
                "vector_column": column_name,
                "dimension": dimension,
                "row_count": row_count
            }
            
            # Sample metadata if available
            if row_count > 0 and not quiet:
                sample_query = f"""
                SELECT * FROM "{schema_name}"."{table_name}" LIMIT 1;
                """
                
                sample = await connector.fetch_one(sample_query)
                if sample:
                    print(f"  Sample record (excluding vector data):")
                    for key, value in sample.items():
                        if key != column_name:  # Skip the vector data itself
                            # Truncate long values
                            if isinstance(value, (str, list, dict)) and str(value).__len__() > 100:
                                print(f"    {key}: {str(value)[:100]}... (truncated)")
                            else:
                                print(f"    {key}: {value}")
        except Exception as e:
            if not quiet:
                print(f"  Error querying vector table: {e}")
    
    return vector_table_info

async def check_frame_data(connector, frame_path=None, quiet=False):
    """Check if a specific frame is in the database."""
    
    if not frame_path:
        if not quiet:
            print("\n=== No specific frame path provided for lookup ===")
        return False
    
    if not quiet:
        print(f"\n=== Checking for frame data: {frame_path} ===\n")
    
    # Find tables that might contain frame data
    tables_query = """
    SELECT n.nspname as schema, c.relname as table, a.attname as column
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE a.attname IN ('frame_path', 'frame_id', 'path', 'filename')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY n.nspname, c.relname;
    """
    
    potential_tables = await connector.fetch_all(tables_query)
    
    if not potential_tables:
        if not quiet:
            print("No tables with frame path columns found.")
        return False
    
    frame_found = False
    frame_data = {}
    
    for table in potential_tables:
        schema_name = table['schema']
        table_name = table['table']
        column_name = table['column']
        
        # Search for the frame in this table
        frame_basename = os.path.basename(frame_path)
        frame_query = f"""
        SELECT * FROM "{schema_name}"."{table_name}" 
        WHERE "{column_name}" LIKE '%{frame_basename}%'
        LIMIT 1;
        """
        
        try:
            result = await connector.fetch_one(frame_query)
            
            if result:
                frame_found = True
                if not quiet:
                    print(f"Frame found in {schema_name}.{table_name}:")
                    for key, value in result.items():
                        # Skip vector data and truncate long values
                        if key.lower() == 'embedding' or key.lower() == 'vector':
                            print(f"  {key}: <vector data>")
                        elif isinstance(value, (str, list, dict)) and str(value).__len__() > 100:
                            print(f"  {key}: {str(value)[:100]}... (truncated)")
                        else:
                            print(f"  {key}: {value}")
                
                frame_data[f"{schema_name}.{table_name}"] = {
                    "schema": schema_name,
                    "table": table_name,
                    "id_column": column_name,
                    "record_count": 1
                }
        except Exception as e:
            if not quiet:
                print(f"Error searching in {schema_name}.{table_name}: {e}")
    
    if not frame_found and not quiet:
        print(f"Frame '{frame_path}' not found in any database table.")
    
    return frame_found

async def find_duplicate_frames(connector, quiet=False):
    """Find duplicate frames in the database based on path/filename."""
    
    if not quiet:
        print("\n=== Checking for Duplicate Frames ===\n")
    
    # Find all tables with frame_path-like columns
    tables_query = """
    SELECT n.nspname as schema, c.relname as table, a.attname as column
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE a.attname IN ('frame_path', 'frame_id', 'path', 'filename')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY n.nspname, c.relname;
    """
    
    tables = await connector.fetch_all(tables_query)
    
    if not tables:
        if not quiet:
            print("No tables with frame path columns found.")
        return {}
    
    duplicates = {}
    
    for table in tables:
        schema_name = table['schema']
        table_name = table['table']
        column_name = table['column']
        
        # Find duplicate entries in this table
        dupe_query = f"""
        SELECT "{column_name}", COUNT(*) as count
        FROM "{schema_name}"."{table_name}"
        GROUP BY "{column_name}"
        HAVING COUNT(*) > 1
        ORDER BY count DESC;
        """
        
        dupes = await connector.fetch_all(dupe_query)
        
        if dupes:
            if not quiet:
                print(f"Found {len(dupes)} duplicate frame entries in {schema_name}.{table_name}")
                for i, dupe in enumerate(dupes[:5], 1):  # Show top 5
                    frame = dupe[column_name]
                    count = dupe['count']
                    print(f"  {i}. {os.path.basename(str(frame))} - {count} duplicates")
                
                if len(dupes) > 5:
                    print(f"  ... and {len(dupes) - 5} more")
            
            duplicates[f"{schema_name}.{table_name}"] = {
                "schema": schema_name,
                "table": table_name,
                "id_column": column_name,
                "duplicate_count": len(dupes),
                "duplicates": [
                    {
                        "frame": dupe[column_name],
                        "count": dupe["count"]
                    } for dupe in dupes
                ]
            }
    
    return duplicates

async def find_duplicate_chunks(connector, quiet=False):
    """Find duplicate text chunks in the database based on content hash."""
    
    if not quiet:
        print("\n=== Checking for Duplicate Chunks ===\n")
    
    # Find tables that might contain text chunks
    tables_query = """
    SELECT n.nspname as schema, c.relname as table, a.attname as column
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE a.attname IN ('content', 'text', 'chunk_text', 'chunk_content')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY n.nspname, c.relname;
    """
    
    tables = await connector.fetch_all(tables_query)
    
    if not tables:
        if not quiet:
            print("No tables with text chunk columns found.")
        return {}
    
    duplicates = {}
    total_chunk_count = 0
    total_unique_content = 0
    
    for table in tables:
        schema_name = table['schema']
        table_name = table['table']
        column_name = table['column']
        
        # First check if the table has a content_hash column for efficient checking
        columns_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = '{schema_name}'
        AND table_name = '{table_name}'
        AND column_name IN ('content_hash', 'hash', 'md5', 'checksum')
        """
        
        hash_columns = await connector.fetch_all(columns_query)
        hash_column = hash_columns[0]['column_name'] if hash_columns else None
        
        if hash_column:
            # If we have a hash column, use it for finding duplicates
            if not quiet:
                print(f"Found hash column '{hash_column}' in {schema_name}.{table_name}")
            
            dupe_query = f"""
            SELECT "{hash_column}", COUNT(*) as count
            FROM "{schema_name}"."{table_name}"
            WHERE "{hash_column}" IS NOT NULL
            GROUP BY "{hash_column}"
            HAVING COUNT(*) > 1
            ORDER BY count DESC;
            """
            
            dupes = await connector.fetch_all(dupe_query)
            
            # Also get total counts
            count_query = f"""
            SELECT COUNT(*) as total, COUNT(DISTINCT "{hash_column}") as unique
            FROM "{schema_name}"."{table_name}"
            WHERE "{hash_column}" IS NOT NULL;
            """
            
            count_result = await connector.fetch_one(count_query)
            this_total = count_result['total'] if count_result else 0
            this_unique = count_result['unique'] if count_result else 0
            
            total_chunk_count += this_total
            total_unique_content += this_unique
            
            if dupes:
                if not quiet:
                    print(f"Found {len(dupes)} sets of duplicate chunks in {schema_name}.{table_name}")
                    print(f"Total chunks: {this_total}, Unique content: {this_unique}")
                    
                    for i, dupe in enumerate(dupes[:5], 1):
                        hash_val = dupe[hash_column]
                        count = dupe['count']
                        print(f"  {i}. Hash {hash_val[:8]}... - {count} duplicates")
                    
                    if len(dupes) > 5:
                        print(f"  ... and {len(dupes) - 5} more sets of duplicates")
                
                duplicates[f"{schema_name}.{table_name}"] = {
                    "schema": schema_name,
                    "table": table_name,
                    "content_column": column_name,
                    "hash_column": hash_column,
                    "duplicate_sets": len(dupes),
                    "total_duplicates": sum(d['count'] - 1 for d in dupes),
                    "total_chunks": this_total,
                    "unique_content": this_unique,
                    "duplicates": [
                        {
                            "content_hash": d[hash_column],
                            "count": d['count']
                        } for d in dupes
                    ]
                }
        else:
            # No hash column, need to compute hashes ourselves
            try:
                # First fetch all content (limiting to avoid memory issues)
                all_chunks_query = f"""
                SELECT id, "{column_name}" as content
                FROM "{schema_name}"."{table_name}"
                WHERE "{column_name}" IS NOT NULL
                LIMIT 10000;
                """
                
                chunks = await connector.fetch_all(all_chunks_query)
                
                if not chunks:
                    if not quiet:
                        print(f"No chunks found in {schema_name}.{table_name}")
                    continue
                
                # Compute content hashes
                chunk_hashes = {}
                for chunk in chunks:
                    if not chunk['content']:
                        continue
                    content_hash = hashlib.md5(str(chunk['content']).encode('utf-8')).hexdigest()
                    if content_hash not in chunk_hashes:
                        chunk_hashes[content_hash] = []
                    chunk_hashes[content_hash].append(chunk['id'])
                
                # Find duplicate hashes
                duplicate_chunks = {h: ids for h, ids in chunk_hashes.items() if len(ids) > 1}
                
                # Update totals
                this_total = len(chunks)
                this_unique = len(chunk_hashes)
                total_chunk_count += this_total
                total_unique_content += this_unique
                
                if duplicate_chunks:
                    if not quiet:
                        print(f"Found {len(duplicate_chunks)} sets of duplicate chunks in {schema_name}.{table_name}")
                        print(f"Total chunks: {this_total}, Unique content: {this_unique}")
                        
                        for i, (hash_val, ids) in enumerate(list(duplicate_chunks.items())[:5], 1):
                            print(f"  {i}. Hash {hash_val[:8]}... - {len(ids)} duplicates (IDs: {', '.join(str(id) for id in ids[:3])}...)")
                        
                        if len(duplicate_chunks) > 5:
                            print(f"  ... and {len(duplicate_chunks) - 5} more sets of duplicates")
                    
                    duplicates[f"{schema_name}.{table_name}"] = {
                        "schema": schema_name,
                        "table": table_name,
                        "content_column": column_name,
                        "hash_column": None,
                        "duplicate_sets": len(duplicate_chunks),
                        "total_duplicates": sum(len(ids) - 1 for ids in duplicate_chunks.values()),
                        "total_chunks": this_total,
                        "unique_content": this_unique,
                        "duplicates": [
                            {
                                "content_hash": hash_val,
                                "ids": ids,
                                "count": len(ids)
                            } for hash_val, ids in duplicate_chunks.items()
                        ]
                    }
            except Exception as e:
                if not quiet:
                    print(f"Error checking for duplicate chunks in {schema_name}.{table_name}: {e}")
    
    # Print summary
    if not quiet:
        if duplicates:
            print(f"\nSummary: Found duplicates in {len(duplicates)} tables")
            print(f"Total chunks analyzed: {total_chunk_count}")
            print(f"Unique content: {total_unique_content}")
            print(f"Duplicate content: {total_chunk_count - total_unique_content}")
        else:
            print("No duplicate chunks found in any table")
    
    return duplicates

async def remove_duplicate_frames(connector, duplicates, dry_run=True, quiet=False):
    """Remove duplicate frames from the database, keeping only one instance of each."""
    
    if not duplicates:
        if not quiet:
            print("No duplicates to remove")
        return
    
    if not quiet:
        print("\n=== Removing Duplicate Frames ===\n")
    
    for table_key, table_info in duplicates.items():
        schema_name = table_info["schema"]
        table_name = table_info["table"]
        id_column = table_info["id_column"]
        
        if not quiet:
            print(f"Processing table: {schema_name}.{table_name}")
        
        for dupe in table_info["duplicates"]:
            frame_path = dupe["frame"]
            count = dupe["count"]
            
            if not frame_path:
                if not quiet:
                    print(f"  Skipping empty frame path")
                continue
            
            # Find all records for this frame
            records_query = f"""
            SELECT id FROM "{schema_name}"."{table_name}"
            WHERE "{id_column}" = $1
            ORDER BY id;
            """
            
            records = await connector.fetch_all(records_query, frame_path)
            
            if not records or len(records) <= 1:
                continue  # No duplicates
            
            # Keep the first record, delete the rest
            keep_id = records[0]["id"]
            delete_ids = [r["id"] for r in records[1:]]
            
            if not quiet:
                print(f"  {os.path.basename(str(frame_path))}: keeping ID {keep_id}, removing {len(delete_ids)} duplicates")
            
            if not dry_run:
                # Execute the delete
                delete_query = f"""
                DELETE FROM "{schema_name}"."{table_name}"
                WHERE id = ANY($1::bigint[]);
                """
                
                try:
                    result = await connector.execute(delete_query, delete_ids)
                    if not quiet:
                        print(f"    Deleted {result} records")
                except Exception as e:
                    if not quiet:
                        print(f"    Error deleting duplicates: {e}")
            else:
                if not quiet:
                    print(f"    [DRY RUN] Would delete IDs: {', '.join(str(id) for id in delete_ids[:5])}{' and more' if len(delete_ids) > 5 else ''}")

async def remove_duplicate_chunks(connector, duplicates, dry_run=True, quiet=False):
    """Remove duplicate chunks from the database, keeping only one instance of each set."""
    
    if not duplicates:
        if not quiet:
            print("No duplicate chunks to remove")
        return
    
    if not quiet:
        print("\n=== Removing Duplicate Chunks ===\n")
    
    for table_key, table_info in duplicates.items():
        schema_name = table_info["schema"]
        table_name = table_info["table"]
        
        if not quiet:
            print(f"Processing table: {schema_name}.{table_name}")
        
        for dupe_set in table_info["duplicates"]:
            content_hash = dupe_set["content_hash"]
            ids = dupe_set["ids"]
            
            if len(ids) <= 1:
                continue  # No duplicates
            
            # Keep the first ID, delete the rest
            keep_id = ids[0]
            delete_ids = ids[1:]
            
            if not quiet:
                print(f"  Hash {content_hash[:8]}...: keeping ID {keep_id}, removing {len(delete_ids)} duplicates")
            
            if not dry_run:
                # Execute the delete
                delete_query = f"""
                DELETE FROM "{schema_name}"."{table_name}"
                WHERE id = ANY($1::bigint[]);
                """
                
                try:
                    result = await connector.execute(delete_query, delete_ids)
                    if not quiet:
                        print(f"    Deleted {result} records")
                except Exception as e:
                    if not quiet:
                        print(f"    Error deleting duplicate chunks: {e}")
            else:
                if not quiet:
                    print(f"    [DRY RUN] Would delete IDs: {', '.join(str(id) for id in delete_ids[:5])}{' and more' if len(delete_ids) > 5 else ''}")

async def main():
    parser = argparse.ArgumentParser(description='Check database structure and frame data')
    parser.add_argument('--frame', type=str, help='Check if a specific frame path exists in the database')
    parser.add_argument('--output', type=str, help='Save results to a JSON file')
    parser.add_argument('--check-duplicates', action='store_true', help='Check for duplicate frames and chunks')
    parser.add_argument('--remove-duplicates', action='store_true', help='Remove duplicate frames and chunks (use with caution)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be removed without actually removing')
    parser.add_argument('--quiet', action='store_true', help='Minimize output (for use in scripts)')
    args = parser.parse_args()
    
    # Get database credentials from environment
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'framestore'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    try:
        # Initialize database connector
        connector = PostgresConnector(**db_config)
        await connector.connect()
        
        if not args.quiet:
            print("\n===== DATABASE STRUCTURE VERIFICATION =====")
            print(f"Database: {db_config['database']} at {db_config['host']}:{db_config['port']}")
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
        
        # Store results for JSON output
        results = {
            'timestamp': datetime.now().isoformat(),
            'database': db_config['database'],
            'host': db_config['host'],
        }
        
        # Check for specific frame if provided
        frame_found = False
        if args.frame:
            frame_found = await check_frame_data(connector, args.frame, args.quiet)
            results['frame_check'] = {
                'frame': args.frame,
                'found': frame_found
            }
            
            # Return with appropriate exit code for scripts to use
            if not args.check_duplicates and not args.output:
                sys.exit(0 if frame_found else 1)
        
        # Check database tables and structure
        if not args.frame or args.output or args.check_duplicates:
            schema_tables = await check_tables(connector, args.quiet)
            results['schemas'] = schema_tables
            
            # Check vector tables
            vector_tables = await check_vector_tables(connector, args.quiet)
            results['vector_tables'] = vector_tables
        
        # Check for duplicate frames and chunks if requested
        if args.check_duplicates or args.remove_duplicates:
            # Find duplicate frames
            duplicate_frames = await find_duplicate_frames(connector, args.quiet)
            results['duplicate_frames'] = duplicate_frames
            
            # Find duplicate chunks
            duplicate_chunks = await find_duplicate_chunks(connector, args.quiet)
            results['duplicate_chunks'] = duplicate_chunks
            
            # Remove duplicates if requested
            if args.remove_duplicates:
                await remove_duplicate_frames(connector, duplicate_frames, args.dry_run, args.quiet)
                await remove_duplicate_chunks(connector, duplicate_chunks, args.dry_run, args.quiet)
        
        # Save results to JSON if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            
            if not args.quiet:
                print(f"\nResults saved to: {args.output}")
        
        if not args.quiet:
            print("\n===== Database check complete =====")
        
    except Exception as e:
        if not args.quiet:
            print(f"Error connecting to database: {e}")
        sys.exit(1)
    finally:
        # Close the connection
        if 'connector' in locals():
            await connector.close()

if __name__ == "__main__":
    asyncio.run(main()) 