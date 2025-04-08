#!/usr/bin/env python
"""
Duplicate Checking Script

This script checks for duplicate frames and chunks in both:
1. Local CSV storage
2. Database (if connected)

Usage:
  python check_duplicates.py --frame <frame_path> [--quiet]
  python check_duplicates.py --check-local [--chunk-hash <hash>]
  python check_duplicates.py --check-db [--chunk-hash <hash>]
  python check_duplicates.py --list-stats
"""

import os
import sys
import argparse
import asyncio
import json
import hashlib
import csv
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Constants
DEFAULT_STORAGE_DIR = "all_frame_embeddings"

async def check_duplicates(frame_path=None, chunk_hash=None, check_local=True, check_db=True, 
                          storage_dir=DEFAULT_STORAGE_DIR, quiet=False, list_stats=False):
    """Check for duplicates in both local storage and database."""
    
    results = {
        "local": {
            "frame_found": False, 
            "chunk_found": False,
            "details": {}
        },
        "database": {
            "frame_found": False,
            "chunk_found": False,
            "details": {}
        }
    }
    
    # Check local storage first
    if check_local:
        local_results = check_local_storage(frame_path, chunk_hash, storage_dir, quiet, list_stats)
        results["local"] = local_results
        
        # If we found matches locally and we're just checking existence, we can exit early
        if frame_path and local_results["frame_found"] and not list_stats:
            if not quiet:
                print(f"Frame found in local storage: {frame_path}")
            return True, results
        
        if chunk_hash and local_results["chunk_found"] and not list_stats:
            if not quiet:
                print(f"Chunk found in local storage: {chunk_hash}")
            return True, results
    
    # Check database if needed
    if check_db:
        try:
            db_results = await check_database(frame_path, chunk_hash, quiet, list_stats)
            results["database"] = db_results
            
            # If we found matches in the database
            if frame_path and db_results["frame_found"] and not list_stats:
                if not quiet:
                    print(f"Frame found in database: {frame_path}")
                return True, results
                
            if chunk_hash and db_results["chunk_found"] and not list_stats:
                if not quiet:
                    print(f"Chunk found in database: {chunk_hash}")
                return True, results
        except Exception as e:
            if not quiet:
                print(f"Error checking database: {e}")
            results["database"]["error"] = str(e)
    
    # If we're just listing stats, return all results
    if list_stats:
        return True, results
    
    # If we got here, the frame/chunk wasn't found
    if frame_path and not quiet:
        print(f"Frame not found: {frame_path}")
    
    if chunk_hash and not quiet:
        print(f"Chunk not found: {chunk_hash}")
    
    return False, results

def check_local_storage(frame_path=None, chunk_hash=None, storage_dir=DEFAULT_STORAGE_DIR, 
                        quiet=False, list_stats=False):
    """Check for duplicates in local CSV storage."""
    
    results = {
        "frame_found": False,
        "chunk_found": False,
        "details": {}
    }
    
    frames_csv = os.path.join(storage_dir, "payloads", "csv", "processed_frames.csv")
    chunks_csv = os.path.join(storage_dir, "payloads", "csv", "frame_chunks.csv")
    
    # Check if the CSV files exist
    if not os.path.exists(frames_csv) or not os.path.exists(chunks_csv):
        if not quiet:
            print(f"Local CSV files not found in {storage_dir}")
        return results
    
    # Collect statistics if requested
    if list_stats:
        # Count total frames
        with open(frames_csv, 'r') as f:
            frame_reader = csv.reader(f)
            next(frame_reader)  # Skip header
            frame_count = sum(1 for row in frame_reader)
        
        # Count total chunks
        with open(chunks_csv, 'r') as f:
            chunk_reader = csv.reader(f)
            next(chunk_reader)  # Skip header
            chunk_count = sum(1 for row in chunk_reader)
        
        # Count unique frames and chunks by processing the files
        unique_frames = set()
        with open(frames_csv, 'r') as f:
            frame_reader = csv.reader(f)
            next(frame_reader)  # Skip header
            for row in frame_reader:
                if len(row) >= 4:  # Ensure we have at least frame_id
                    frame_id = row[3].strip('"')
                    unique_frames.add(frame_id)
        
        unique_chunks = set()
        with open(chunks_csv, 'r') as f:
            chunk_reader = csv.reader(f)
            next(chunk_reader)  # Skip header
            for row in chunk_reader:
                if len(row) >= 3:  # Ensure we have chunk_hash
                    chunk_hash_val = row[2].strip('"')
                    unique_chunks.add(chunk_hash_val)
        
        results["details"] = {
            "total_frames": frame_count,
            "unique_frames": len(unique_frames),
            "total_chunks": chunk_count,
            "unique_chunks": len(unique_chunks),
            "frames_csv": frames_csv,
            "chunks_csv": chunks_csv
        }
        
        if not quiet:
            print("\n=== Local Storage Statistics ===")
            print(f"Frames: {frame_count} total, {len(unique_frames)} unique")
            print(f"Chunks: {chunk_count} total, {len(unique_chunks)} unique")
            print(f"CSV Files: {frames_csv}, {chunks_csv}")
        
        return results
    
    # Check for a specific frame if provided
    if frame_path:
        frame_filename = os.path.basename(frame_path)
        frame_id = os.path.splitext(frame_filename)[0]
        
        with open(frames_csv, 'r') as f:
            frame_reader = csv.reader(f)
            next(frame_reader)  # Skip header
            for row in frame_reader:
                if len(row) >= 1:
                    # Remove quotes if present
                    csv_path = row[0].strip('"')
                    if frame_path in csv_path or csv_path in frame_path or frame_filename in csv_path:
                        results["frame_found"] = True
                        
                        # Add details if we have them
                        if len(row) >= 5:
                            results["details"]["frame"] = {
                                "path": csv_path,
                                "processed_time": row[1].strip('"'),
                                "status": row[2].strip('"'),
                                "frame_id": row[3].strip('"') if len(row) > 3 else "",
                                "metadata_size": row[4].strip('"') if len(row) > 4 else ""
                            }
                        break
        
        # If frame was found, also check for its chunks
        if results["frame_found"]:
            frame_chunks = []
            with open(chunks_csv, 'r') as f:
                chunk_reader = csv.reader(f)
                next(chunk_reader)  # Skip header
                for row in chunk_reader:
                    if len(row) >= 1 and row[0].strip('"') == frame_id:
                        frame_chunks.append({
                            "index": row[1].strip('"') if len(row) > 1 else "",
                            "hash": row[2].strip('"') if len(row) > 2 else "",
                            "length": row[3].strip('"') if len(row) > 3 else "",
                            "processed_time": row[4].strip('"') if len(row) > 4 else ""
                        })
            
            if frame_chunks:
                results["details"]["chunks"] = frame_chunks
                if not quiet:
                    print(f"Found {len(frame_chunks)} chunks for frame {frame_id} in local storage")
    
    # Check for a specific chunk hash if provided
    if chunk_hash:
        with open(chunks_csv, 'r') as f:
            chunk_reader = csv.reader(f)
            next(chunk_reader)  # Skip header
            for row in chunk_reader:
                if len(row) >= 3 and row[2].strip('"') == chunk_hash:
                    results["chunk_found"] = True
                    
                    # Add details
                    chunk_details = {
                        "frame_id": row[0].strip('"'),
                        "index": row[1].strip('"'),
                        "hash": row[2].strip('"'),
                        "length": row[3].strip('"') if len(row) > 3 else "",
                        "processed_time": row[4].strip('"') if len(row) > 4 else ""
                    }
                    
                    # If we found the chunk, also look up its frame details
                    with open(frames_csv, 'r') as frame_file:
                        frame_reader = csv.reader(frame_file)
                        next(frame_reader)  # Skip header
                        for frame_row in frame_reader:
                            if len(frame_row) >= 4 and frame_row[3].strip('"') == chunk_details["frame_id"]:
                                chunk_details["frame_path"] = frame_row[0].strip('"')
                                break
                    
                    results["details"]["chunk"] = chunk_details
                    break
    
    return results

async def check_database(frame_path=None, chunk_hash=None, quiet=False, list_stats=False):
    """Check for duplicates in the database."""
    
    results = {
        "frame_found": False,
        "chunk_found": False,
        "details": {}
    }
    
    # Import database connector
    try:
        from src.connectors.postgres_connector import PostgresConnector
    except ImportError:
        try:
            # Try alternative import paths
            sys.path.append(str(project_root / "src"))
            from connectors.postgres_connector import PostgresConnector
        except ImportError:
            if not quiet:
                print("Error: Could not import PostgresConnector. Database checks disabled.")
            results["error"] = "PostgresConnector import failed"
            return results
    
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
        
        # Import the check_database.py functions if available
        db_check_script = script_dir / "check_database.py"
        if db_check_script.exists():
            sys.path.insert(0, str(script_dir))
            try:
                from check_database import check_frame_data, check_tables, check_vector_tables
                
                # Collect statistics if requested
                if list_stats:
                    schema_tables = await check_tables(connector, quiet=True)
                    vector_tables = await check_vector_tables(connector, quiet=True)
                    
                    # Prepare results
                    results["details"] = {
                        "schemas": schema_tables,
                        "vector_tables": vector_tables
                    }
                    
                    if not quiet:
                        print("\n=== Database Statistics ===")
                        total_tables = sum(len(tables) for tables in schema_tables.values())
                        print(f"Schemas: {len(schema_tables)}")
                        print(f"Tables: {total_tables}")
                        print(f"Vector tables: {len(vector_tables)}")
                        
                        # Print some frame/chunk counts if available
                        for schema, tables in schema_tables.items():
                            for table in tables:
                                if "frame" in table.lower():
                                    count_query = f"""
                                    SELECT COUNT(*) as count FROM "{schema}"."{table}";
                                    """
                                    try:
                                        count_result = await connector.fetch_one(count_query)
                                        count = count_result['count'] if count_result else 0
                                        print(f"  {schema}.{table}: {count} rows")
                                    except:
                                        pass
                    
                    await connector.close()
                    return results
                
                # Check for specific frame
                if frame_path:
                    frame_found = await check_frame_data(connector, frame_path, quiet=True)
                    results["frame_found"] = frame_found
                    
                    if frame_found and not quiet:
                        print(f"Frame found in database: {frame_path}")
                
                # Check for specific chunk hash
                if chunk_hash:
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
                    
                    for table in tables:
                        schema_name = table['schema']
                        table_name = table['table']
                        column_name = table['column']
                        
                        # Try to find chunks by content hash
                        chunks_query = f"""
                        SELECT id, {column_name} as content
                        FROM "{schema_name}"."{table_name}"
                        LIMIT 100;
                        """
                        
                        try:
                            chunks = await connector.fetch_all(chunks_query)
                            
                            for chunk in chunks:
                                if not chunk['content']:
                                    continue
                                    
                                # Compute hash and compare
                                content_hash = hashlib.md5(str(chunk['content']).encode('utf-8')).hexdigest()
                                if content_hash == chunk_hash:
                                    results["chunk_found"] = True
                                    results["details"]["chunk"] = {
                                        "id": chunk['id'],
                                        "schema": schema_name,
                                        "table": table_name,
                                        "hash": chunk_hash
                                    }
                                    
                                    if not quiet:
                                        print(f"Chunk found in database: {schema_name}.{table_name}, ID: {chunk['id']}")
                                    
                                    break
                            
                            if results["chunk_found"]:
                                break
                                
                        except Exception as e:
                            if not quiet:
                                print(f"Error searching chunks in {schema_name}.{table_name}: {e}")
            except ImportError as e:
                if not quiet:
                    print(f"Could not import functions from check_database.py: {e}")
                
                # Fallback to direct database queries for frame check
                if frame_path:
                    frame_filename = os.path.basename(frame_path)
                    
                    # Find tables that might contain frame data
                    tables_query = """
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_name LIKE '%frame%'
                    AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                    """
                    
                    tables = await connector.fetch_all(tables_query)
                    
                    for table in tables:
                        schema = table['table_schema']
                        table_name = table['table_name']
                        
                        # Check if table has a path or filename column
                        columns_query = f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = '{schema}'
                        AND table_name = '{table_name}'
                        AND (column_name LIKE '%path%' OR column_name LIKE '%file%')
                        """
                        
                        columns = await connector.fetch_all(columns_query)
                        
                        for column in columns:
                            column_name = column['column_name']
                            
                            # Search for the frame
                            query = f"""
                            SELECT * FROM "{schema}"."{table_name}"
                            WHERE "{column_name}" LIKE '%{frame_filename}%'
                            LIMIT 1
                            """
                            
                            try:
                                result = await connector.fetch_one(query)
                                if result:
                                    results["frame_found"] = True
                                    results["details"]["frame"] = {
                                        "schema": schema,
                                        "table": table_name,
                                        "column": column_name
                                    }
                                    
                                    if not quiet:
                                        print(f"Frame found in database: {schema}.{table_name}")
                                    
                                    break
                            except:
                                pass
                        
                        if results["frame_found"]:
                            break
        else:
            if not quiet:
                print("check_database.py not found, using direct database queries.")
            
            # Implement basic queries here similar to the fallback above
            
    except Exception as e:
        if not quiet:
            print(f"Error connecting to database: {e}")
        results["error"] = str(e)
    finally:
        # Close the connection
        if 'connector' in locals():
            await connector.close()
    
    return results

async def main():
    parser = argparse.ArgumentParser(description='Check for duplicate frames and chunks in local storage and database')
    parser.add_argument('--frame', type=str, help='Check if a specific frame path exists')
    parser.add_argument('--chunk-hash', type=str, help='Check if a specific chunk hash exists')
    parser.add_argument('--check-local', action='store_true', help='Only check local storage')
    parser.add_argument('--check-db', action='store_true', help='Only check database')
    parser.add_argument('--storage-dir', type=str, default=DEFAULT_STORAGE_DIR, help='Path to local storage directory')
    parser.add_argument('--output', type=str, help='Save results to a JSON file')
    parser.add_argument('--list-stats', action='store_true', help='List statistics about frames and chunks')
    parser.add_argument('--quiet', action='store_true', help='Minimize output')
    args = parser.parse_args()
    
    # Determine which checks to run
    check_local = True
    check_db = True
    
    if args.check_local and not args.check_db:
        check_db = False
    elif args.check_db and not args.check_local:
        check_local = False
    
    # Run the checks
    found, results = await check_duplicates(
        frame_path=args.frame,
        chunk_hash=args.chunk_hash,
        check_local=check_local,
        check_db=check_db,
        storage_dir=args.storage_dir,
        quiet=args.quiet,
        list_stats=args.list_stats
    )
    
    # Save results to JSON if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        if not args.quiet:
            print(f"\nResults saved to: {args.output}")
    
    # Exit with status code for scripting
    sys.exit(0 if found or args.list_stats else 1)

if __name__ == "__main__":
    asyncio.run(main()) 