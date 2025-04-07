#!/usr/bin/env python
"""
Database Structure Verification Script

This script connects to the PostgreSQL database and checks:
1. That the database exists and is accessible
2. What schemas and tables contain frame data
3. How many records exist in each table
4. Sample data from each table to verify structure
"""

import os
import sys
import argparse
import asyncio
import json
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

async def check_tables(connector):
    """Check all tables in the database and report on their contents."""
    
    print("\n=== Database Structure Check ===\n")
    
    # Get a list of all schemas
    schemas_query = """
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY schema_name;
    """
    
    schemas = await connector.fetch_all(schemas_query)
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
                    
                    if frame_related:
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
                print(f"    Error querying table: {e}")
    
    return schema_tables

async def check_vector_tables(connector):
    """Specifically check for pgvector tables and their contents."""
    
    print("\n=== Vector Storage Tables ===\n")
    
    # Check for the pgvector extension
    extension_query = """
    SELECT * FROM pg_extension WHERE extname = 'vector';
    """
    
    extension = await connector.fetch_one(extension_query)
    if not extension:
        print("pgvector extension is NOT installed in this database.")
        return
    
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
        print("No tables with vector columns found.")
        return
    
    print(f"Found {len(vector_tables)} tables with vector columns:")
    
    for vt in vector_tables:
        schema_name = vt['schema']
        table_name = vt['table']
        column_name = vt['column']
        
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
            if dim_result:
                dimension = dim_result['dimension']
                print(f"  Vector dimension: {dimension}")
            
            # Count records
            count_query = f"""
            SELECT COUNT(*) as count FROM "{schema_name}"."{table_name}";
            """
            
            count_result = await connector.fetch_one(count_query)
            row_count = count_result['count'] if count_result else 0
            
            print(f"  Total records: {row_count}")
            
            # Sample metadata if available
            if row_count > 0:
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
            print(f"  Error querying vector table: {e}")

async def check_frame_data(connector, frame_path=None):
    """Check if a specific frame is in the database."""
    
    if not frame_path:
        print("\n=== No specific frame path provided for lookup ===")
        return
    
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
        print("No tables with frame path columns found.")
        return
    
    frame_found = False
    
    for table in potential_tables:
        schema_name = table['schema']
        table_name = table['table']
        column_name = table['column']
        
        # Search for the frame in this table
        frame_query = f"""
        SELECT * FROM "{schema_name}"."{table_name}" 
        WHERE "{column_name}" LIKE '%{os.path.basename(frame_path)}%'
        LIMIT 1;
        """
        
        try:
            result = await connector.fetch_one(frame_query)
            
            if result:
                frame_found = True
                print(f"Frame found in {schema_name}.{table_name}:")
                for key, value in result.items():
                    # Skip vector data and truncate long values
                    if key.lower() == 'embedding' or key.lower() == 'vector':
                        print(f"  {key}: <vector data>")
                    elif isinstance(value, (str, list, dict)) and str(value).__len__() > 100:
                        print(f"  {key}: {str(value)[:100]}... (truncated)")
                    else:
                        print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error searching in {schema_name}.{table_name}: {e}")
    
    if not frame_found:
        print(f"Frame '{frame_path}' not found in any database table.")

async def main():
    parser = argparse.ArgumentParser(description='Check database structure and frame data')
    parser.add_argument('--frame', type=str, help='Check if a specific frame path exists in the database')
    parser.add_argument('--output', type=str, help='Save results to a JSON file')
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
        
        print("\n===== DATABASE STRUCTURE VERIFICATION =====")
        print(f"Database: {db_config['database']} at {db_config['host']}:{db_config['port']}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Check database tables and structure
        schema_tables = await check_tables(connector)
        
        # Check vector tables
        await check_vector_tables(connector)
        
        # Check for specific frame if provided
        if args.frame:
            await check_frame_data(connector, args.frame)
        
        # Save results to JSON if output file specified
        if args.output:
            result = {
                'timestamp': datetime.now().isoformat(),
                'database': db_config['database'],
                'host': db_config['host'],
                'schemas': schema_tables,
            }
            
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\nResults saved to: {args.output}")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Close the connection
        if 'connector' in locals():
            await connector.close()

if __name__ == "__main__":
    asyncio.run(main()) 