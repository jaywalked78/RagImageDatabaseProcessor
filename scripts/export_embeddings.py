#!/usr/bin/env python3
"""
Export Embeddings - Command line tool for exporting embeddings from the database.

This script handles:
1. Querying embeddings from PostgreSQL
2. Exporting embeddings to various formats (JSON, CSV, JSONL)
3. Filtering by metadata fields
"""

import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# Import project modules
from src.database.postgres_vector_store import PostgresVectorStore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("export_embeddings")

def export_to_json(data: List[Dict[str, Any]], output_file: str) -> bool:
    """
    Export embeddings to a JSON file.
    
    Args:
        data: List of embedding records
        output_file: Path to output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(data)} records to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return False

def export_to_jsonl(data: List[Dict[str, Any]], output_file: str) -> bool:
    """
    Export embeddings to a JSONL (JSON Lines) file.
    
    Args:
        data: List of embedding records
        output_file: Path to output file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_file, 'w') as f:
            for record in data:
                f.write(json.dumps(record) + '\n')
        logger.info(f"Exported {len(data)} records to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting to JSONL: {e}")
        return False

def export_to_csv(data: List[Dict[str, Any]], output_file: str, include_vectors: bool = False) -> bool:
    """
    Export embeddings to a CSV file.
    
    Args:
        data: List of embedding records
        output_file: Path to output file
        include_vectors: Whether to include embedding vectors in the export
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not data:
            logger.error("No data to export")
            return False
            
        # Get all possible field names from all records
        fieldnames = set()
        for record in data:
            fieldnames.update(record.keys())
            
            # Explode metadata fields to first level
            if 'metadata' in record and isinstance(record['metadata'], dict):
                for key in record['metadata'].keys():
                    fieldnames.add(f"metadata_{key}")
        
        # Remove embedding vector if not needed
        if not include_vectors and 'embedding' in fieldnames:
            fieldnames.remove('embedding')
            
        fieldnames = sorted(list(fieldnames))
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data:
                row = {}
                for field in fieldnames:
                    if field.startswith('metadata_') and 'metadata' in record:
                        # Extract metadata field
                        meta_field = field.replace('metadata_', '')
                        row[field] = record['metadata'].get(meta_field, '')
                    elif field == 'embedding' and include_vectors:
                        # Format embedding vector as string
                        row[field] = str(record.get(field, []))
                    else:
                        # Regular field
                        row[field] = record.get(field, '')
                writer.writerow(row)
                
        logger.info(f"Exported {len(data)} records to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Export embeddings from the database")
    
    # Query options
    query_group = parser.add_argument_group("Query Options")
    query_group.add_argument("--limit", type=int, default=1000, help="Maximum number of records to export (default: 1000)")
    query_group.add_argument("--filter", help="Filter by metadata field (format: field=value)")
    query_group.add_argument("--from-date", help="Filter records from date (YYYY-MM-DD)")
    query_group.add_argument("--to-date", help="Filter records to date (YYYY-MM-DD)")
    query_group.add_argument("--airtable-id", help="Filter by Airtable record ID")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--output", required=True, help="Output file path")
    output_group.add_argument("--format", choices=['json', 'jsonl', 'csv'], default='json', help="Output format (default: json)")
    output_group.add_argument("--include-vectors", action="store_true", help="Include embedding vectors in the export")
    
    # Database options
    db_group = parser.add_argument_group("Database Options")
    db_group.add_argument("--connection", help="PostgreSQL connection string (default: from environment)")
    
    args = parser.parse_args()
    
    # Initialize PostgreSQL connection
    db = PostgresVectorStore(
        connection_string=args.connection or os.environ.get('POSTGRES_CONNECTION_STRING')
    )
    
    # Build query filters
    filters = {}
    
    if args.filter:
        try:
            field, value = args.filter.split('=', 1)
            filters[field.strip()] = value.strip()
        except ValueError:
            logger.error(f"Invalid filter format: {args.filter}. Use field=value format.")
            return 1
    
    if args.from_date:
        filters['from_date'] = args.from_date
    
    if args.to_date:
        filters['to_date'] = args.to_date
    
    if args.airtable_id:
        filters['airtable_id'] = args.airtable_id
    
    # Query embeddings
    logger.info(f"Querying embeddings with filters: {filters}")
    embeddings = db.query_embeddings(limit=args.limit, filters=filters)
    logger.info(f"Found {len(embeddings)} embedding records")
    
    # Export embeddings
    output_file = args.output
    success = False
    
    if args.format == 'json':
        success = export_to_json(embeddings, output_file)
    elif args.format == 'jsonl':
        success = export_to_jsonl(embeddings, output_file)
    elif args.format == 'csv':
        success = export_to_csv(embeddings, output_file, include_vectors=args.include_vectors)
    
    # Close connection
    db.close()
    
    # Return exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 