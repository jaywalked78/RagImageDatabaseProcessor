#!/usr/bin/env python
"""
Duplicate Frame Processing Checker

This script analyzes local storage and database to detect:
1. Frames that have been processed multiple times
2. Frames that exist locally but not in the database
3. Frames that exist in the database but not locally

It helps identify issues with the frame processing pipeline and ensures data integrity.
"""

import os
import sys
import json
import argparse
import csv
from pathlib import Path
from collections import defaultdict
import asyncio
from datetime import datetime

# Add the project root to the path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Parse command line arguments
parser = argparse.ArgumentParser(description='Check for duplicate frame processing')
parser.add_argument('--storage-dir', type=str, default='all_frame_embeddings',
                    help='Directory where processed frames are stored')
parser.add_argument('--csv-file', type=str,
                    help='Custom CSV file to check (default is <storage-dir>/payloads/csv/processed_frames.csv)')
parser.add_argument('--detailed', action='store_true',
                    help='Show detailed information for each duplicate')
parser.add_argument('--check-db', action='store_true',
                    help='Check database for duplicates (requires database connection)')
parser.add_argument('--output', type=str, help='Save results to a JSON file')
args = parser.parse_args()

def find_json_files(storage_dir):
    """Find all JSON files in the storage directory."""
    json_dir = Path(storage_dir) / 'payloads' / 'json'
    
    if not json_dir.exists():
        print(f"JSON directory not found: {json_dir}")
        return []
    
    return list(json_dir.glob('*.json'))

def process_csv_log(csv_path):
    """Process the CSV log file to find duplicate frame processing."""
    if not csv_path.exists():
        print(f"CSV log file not found: {csv_path}")
        return {}
    
    frame_entries = defaultdict(list)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the frame path (might have quotes)
            frame_path = row.get('frame_path', '').strip('"')
            if frame_path:
                timestamp = row.get('processed_time', '').strip('"')
                status = row.get('status', '').strip('"')
                
                frame_entries[frame_path].append({
                    'timestamp': timestamp,
                    'status': status
                })
    
    return frame_entries

def check_local_duplicates(storage_dir, csv_file=None, detailed=False):
    """Check for duplicates in local storage."""
    print("\n=== Checking Local Storage for Duplicates ===\n")
    
    # Determine CSV path
    if csv_file:
        csv_path = Path(csv_file)
    else:
        csv_path = Path(storage_dir) / 'payloads' / 'csv' / 'processed_frames.csv'
    
    # Process JSON files
    json_files = find_json_files(storage_dir)
    print(f"Found {len(json_files)} JSON files in {storage_dir}/payloads/json")
    
    # Process CSV log
    frame_entries = process_csv_log(csv_path)
    print(f"Found {len(frame_entries)} unique frames in CSV log: {csv_path}")
    
    # Check for duplicates in CSV
    duplicates = {frame: entries for frame, entries in frame_entries.items() if len(entries) > 1}
    print(f"Found {len(duplicates)} frames processed multiple times according to CSV log")
    
    if detailed and duplicates:
        print("\nDetailed duplicate information:")
        for frame, entries in duplicates.items():
            print(f"\n- {os.path.basename(frame)}")
            for i, entry in enumerate(entries, 1):
                print(f"  {i}. Processed: {entry['timestamp']} (Status: {entry['status']})")
    
    # Check for JSON files without CSV entries
    json_basenames = {f.stem for f in json_files}
    csv_basenames = {os.path.basename(f).rsplit('.', 1)[0] for f in frame_entries.keys()}
    
    json_only = json_basenames - csv_basenames
    print(f"Found {len(json_only)} JSON files with no corresponding CSV entry")
    
    csv_only = csv_basenames - json_basenames
    print(f"Found {len(csv_only)} CSV entries with no corresponding JSON file")
    
    if detailed:
        if json_only:
            print("\nJSON files with no CSV entry:")
            for i, basename in enumerate(sorted(json_only), 1):
                if i > 20:
                    print(f"  ... and {len(json_only) - 20} more")
                    break
                print(f"  {basename}.json")
        
        if csv_only:
            print("\nCSV entries with no JSON file:")
            for i, basename in enumerate(sorted(csv_only), 1):
                if i > 20:
                    print(f"  ... and {len(csv_only) - 20} more")
                    break
                print(f"  {basename}")
    
    return {
        'total_json_files': len(json_files),
        'total_csv_entries': len(frame_entries),
        'duplicate_entries': len(duplicates),
        'json_only': len(json_only),
        'csv_only': len(csv_only),
        'duplicates': [
            {
                'frame': frame,
                'count': len(entries),
                'entries': entries
            }
            for frame, entries in duplicates.items()
        ] if detailed else []
    }

async def check_db_duplicates(detailed=False):
    """Check for duplicates in the database."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from src.connectors.postgres_connector import PostgresConnector
        
        print("\n=== Checking Database for Duplicates ===\n")
        
        # Get database credentials from environment
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'framestore'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        connector = PostgresConnector(**db_config)
        await connector.connect()
        
        print(f"Connected to database: {db_config['database']} at {db_config['host']}:{db_config['port']}")
        
        # Find all tables with frame_path or similar columns
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
            print("No tables with frame path columns found.")
            return {}
        
        print(f"Found {len(tables)} tables with frame path columns")
        
        result = {}
        
        for table in tables:
            schema_name = table['schema']
            table_name = table['table']
            column_name = table['column']
            
            # Check for duplicates in this table
            duplicate_query = f"""
            SELECT "{column_name}", COUNT(*) as count
            FROM "{schema_name}"."{table_name}"
            GROUP BY "{column_name}"
            HAVING COUNT(*) > 1
            ORDER BY count DESC;
            """
            
            duplicates = await connector.fetch_all(duplicate_query)
            
            # Count total rows
            count_query = f"""
            SELECT COUNT(*) as count FROM "{schema_name}"."{table_name}";
            """
            
            count_result = await connector.fetch_one(count_query)
            total_rows = count_result['count'] if count_result else 0
            
            print(f"\n- Table: {schema_name}.{table_name}")
            print(f"  Total records: {total_rows}")
            print(f"  Duplicate records: {len(duplicates)}")
            
            if detailed and duplicates:
                print(f"  Detailed duplicates:")
                for i, dup in enumerate(duplicates[:10], 1):
                    frame = dup[column_name]
                    count = dup['count']
                    print(f"    {i}. {os.path.basename(str(frame))} ({count} occurrences)")
                
                if len(duplicates) > 10:
                    print(f"    ... and {len(duplicates) - 10} more")
            
            result[f"{schema_name}.{table_name}"] = {
                'total_rows': total_rows,
                'duplicate_count': len(duplicates),
                'duplicates': [
                    {
                        'frame': dup[column_name],
                        'count': dup['count']
                    }
                    for dup in duplicates
                ] if detailed else []
            }
        
        await connector.close()
        return result
        
    except ImportError:
        print("Error: Could not import database connector. Make sure you're running from the project root.")
        return {}
    except Exception as e:
        print(f"Error checking database: {e}")
        return {}

async def main():
    storage_dir = args.storage_dir
    
    # Check local duplicates
    local_results = check_local_duplicates(storage_dir, args.csv_file, args.detailed)
    
    # Check database duplicates if requested
    db_results = {}
    if args.check_db:
        db_results = await check_db_duplicates(args.detailed)
    
    # Compile final results
    results = {
        'timestamp': datetime.now().isoformat(),
        'storage_dir': storage_dir,
        'local_storage': local_results,
        'database': db_results
    }
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    print("\n=== Duplicate Check Complete ===")

if __name__ == "__main__":
    asyncio.run(main()) 