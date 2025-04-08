#!/usr/bin/env python
"""
Database Cleanup Script

This script removes duplicate data from the database:
1. Duplicate frames (keeping only one instance per frame path)
2. Duplicate text chunks (keeping only one instance of identical content)
3. [Optional] Orphaned chunks without associated frames

Use with caution - this script will permanently delete data from the database.
It's recommended to create a database backup before running this script.
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

async def clean_database(dry_run=True, remove_orphans=False, verbose=True):
    """Clean duplicates from the database by calling check_database.py with appropriate flags."""
    
    # Use the check_database.py script to find and remove duplicates
    check_db_script = script_dir / "check_database.py"
    
    if not check_db_script.exists():
        print(f"Error: {check_db_script} not found")
        return False
    
    try:
        # Import functions from check_database.py
        sys.path.insert(0, str(script_dir))
        from check_database import (
            check_tables, check_vector_tables, find_duplicate_frames, 
            find_duplicate_chunks, remove_duplicate_frames, remove_duplicate_chunks
        )
        
        # Get database credentials from environment
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'framestore'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        print(f"\n=== Cleaning Database: {db_config['database']} at {db_config['host']}:{db_config['port']} ===\n")
        
        # Import the PostgresConnector class
        from src.connectors.postgres_connector import PostgresConnector
        
        # Initialize database connector
        connector = PostgresConnector(**db_config)
        await connector.connect()
        
        print("Connected to database successfully")
        
        # Find duplicate frames
        print("\nSearching for duplicate frames...")
        duplicate_frames = await find_duplicate_frames(connector, quiet=not verbose)
        total_frame_dupes = sum(info.get("duplicate_count", 0) for info in duplicate_frames.values())
        
        if total_frame_dupes > 0:
            print(f"Found {total_frame_dupes} duplicate frames across {len(duplicate_frames)} tables")
            
            # Remove duplicate frames
            print("\nRemoving duplicate frames...")
            await remove_duplicate_frames(connector, duplicate_frames, dry_run=dry_run, quiet=not verbose)
            
            if dry_run:
                print("DRY RUN - No frames were actually removed")
            else:
                print(f"Successfully cleaned up duplicate frames")
        else:
            print("No duplicate frames found")
        
        # Find duplicate chunks
        print("\nSearching for duplicate text chunks...")
        duplicate_chunks = await find_duplicate_chunks(connector, quiet=not verbose)
        total_chunk_dupes = sum(info.get("total_duplicates", 0) for info in duplicate_chunks.values())
        
        if total_chunk_dupes > 0:
            print(f"Found {total_chunk_dupes} duplicate chunks across {len(duplicate_chunks)} tables")
            
            # Remove duplicate chunks
            print("\nRemoving duplicate chunks...")
            await remove_duplicate_chunks(connector, duplicate_chunks, dry_run=dry_run, quiet=not verbose)
            
            if dry_run:
                print("DRY RUN - No chunks were actually removed")
            else:
                print(f"Successfully cleaned up duplicate chunks")
        else:
            print("No duplicate chunks found")
        
        # Clean up orphaned chunks if requested
        if remove_orphans:
            print("\nSearching for orphaned chunks...")
            await clean_orphaned_chunks(connector, dry_run=dry_run, verbose=verbose)
        
        # Close the connection
        await connector.close()
        print("\nDatabase cleaning completed successfully")
        return True
        
    except ImportError as e:
        print(f"Error importing functions: {e}")
        return False
    except Exception as e:
        print(f"Error cleaning database: {e}")
        return False

async def clean_orphaned_chunks(connector, dry_run=True, verbose=True):
    """Find and remove chunks that don't have associated frames."""
    
    # Find tables that might contain text chunks
    chunks_query = """
    SELECT 
        c.table_schema as chunk_schema,
        c.table_name as chunk_table,
        c.column_name as frame_ref_column,
        f.table_schema as frame_schema,
        f.table_name as frame_table,
        f.column_name as frame_id_column
    FROM 
        information_schema.columns c
    JOIN 
        information_schema.columns f ON c.column_name LIKE '%frame%id%' OR c.column_name LIKE '%frame%path%'
    WHERE 
        c.table_name LIKE '%chunk%' AND 
        f.table_name LIKE '%frame%' AND
        c.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast') AND
        f.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY c.table_schema, c.table_name;
    """
    
    try:
        potential_tables = await connector.fetch_all(chunks_query)
        
        if not potential_tables:
            print("Could not automatically detect chunk/frame table relationships")
            return
        
        total_orphans = 0
        
        for relation in potential_tables:
            chunk_schema = relation['chunk_schema']
            chunk_table = relation['chunk_table']
            frame_ref_column = relation['frame_ref_column']
            frame_schema = relation['frame_schema']
            frame_table = relation['frame_table']
            frame_id_column = relation['frame_id_column']
            
            # Find orphaned chunks
            orphans_query = f"""
            SELECT c.id
            FROM "{chunk_schema}"."{chunk_table}" c
            LEFT JOIN "{frame_schema}"."{frame_table}" f ON c.{frame_ref_column} = f.{frame_id_column}
            WHERE f.{frame_id_column} IS NULL;
            """
            
            try:
                orphans = await connector.fetch_all(orphans_query)
                
                if orphans:
                    if verbose:
                        print(f"Found {len(orphans)} orphaned chunks in {chunk_schema}.{chunk_table}")
                    
                    total_orphans += len(orphans)
                    
                    if not dry_run:
                        # Delete orphaned chunks
                        orphan_ids = [o['id'] for o in orphans]
                        delete_query = f"""
                        DELETE FROM "{chunk_schema}"."{chunk_table}"
                        WHERE id = ANY($1::bigint[]);
                        """
                        
                        result = await connector.execute(delete_query, orphan_ids)
                        if verbose:
                            print(f"Deleted {result} orphaned chunks")
                    else:
                        if verbose:
                            print(f"DRY RUN - Would delete {len(orphans)} orphaned chunks")
                else:
                    if verbose:
                        print(f"No orphaned chunks found in {chunk_schema}.{chunk_table}")
            except Exception as e:
                print(f"Error checking for orphaned chunks in {chunk_schema}.{chunk_table}: {e}")
        
        print(f"Total orphaned chunks found: {total_orphans}")
        
    except Exception as e:
        print(f"Error cleaning orphaned chunks: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Clean duplicate data from the database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without actually removing")
    parser.add_argument("--remove-orphans", action="store_true", help="Also remove orphaned chunks without associated frames")
    parser.add_argument("--quiet", action="store_true", help="Minimize output")
    args = parser.parse_args()
    
    if not args.dry_run:
        confirmation = input("WARNING: This will permanently delete duplicate data from the database. Continue? [y/N] ")
        if confirmation.lower() != 'y':
            print("Operation cancelled")
            return
    
    await clean_database(dry_run=args.dry_run, remove_orphans=args.remove_orphans, verbose=not args.quiet)

if __name__ == "__main__":
    asyncio.run(main()) 