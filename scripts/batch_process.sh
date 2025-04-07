#!/bin/bash
#
# Batch Process - Process multiple frames in batch mode
# 
# This script processes multiple frames in batch mode, with options for
# parallel or sequential processing, and can save to database or webhook.

# Default settings
INPUT_DIR=""
PATTERN="*.jpg"
LIMIT=0
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CHUNKS=""
SEQUENTIAL=true
WEBHOOK=false
WEBHOOK_PRODUCTION=false
NO_SAVE=false
CSV_FILE="payloads/csv/webhook_payloads.csv"
LOCAL_ONLY=false
LOCAL_STORAGE_DIR="frame_embeddings"

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display help
function show_help {
    echo -e "${BLUE}Database Advanced Tokenizer - Batch Processing${NC}"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -i, --input DIR        Input directory containing frames"
    echo "  -p, --pattern PATTERN  Glob pattern for matching files (default: '*.jpg')"
    echo "  -l, --limit N          Limit processing to N files (default: process all)"
    echo "  -c, --chunk-size N     Size of text chunks (default: 500)"
    echo "  -o, --chunk-overlap N  Overlap between chunks (default: 50)"
    echo "  -m, --max-chunks N     Maximum chunks per frame"
    echo "  -s, --sequential       Process files sequentially (default)"
    echo "  -a, --parallel         Process files in parallel"
    echo "  -w, --webhook          Send data to webhook"
    echo "  -P, --production       Use production webhook (default: test webhook)"
    echo "  -n, --no-save          Don't save payload files"
    echo "  -f, --csv-file FILE    CSV file to store records (default: webhook_payloads.csv)"
    echo "  -L, --local-only       Only store locally, don't send to webhook"
    echo "  -d, --storage-dir DIR  Directory for local storage (default: frame_embeddings)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --input /path/to/frames --pattern '*.jpg' --limit 10 --sequential"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        -p|--pattern)
            PATTERN="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -c|--chunk-size)
            CHUNK_SIZE="$2"
            shift 2
            ;;
        -o|--chunk-overlap)
            CHUNK_OVERLAP="$2"
            shift 2
            ;;
        -m|--max-chunks)
            MAX_CHUNKS="$2"
            shift 2
            ;;
        -s|--sequential)
            SEQUENTIAL=true
            shift
            ;;
        -a|--parallel)
            SEQUENTIAL=false
            shift
            ;;
        -w|--webhook)
            WEBHOOK=true
            shift
            ;;
        -P|--production)
            WEBHOOK_PRODUCTION=true
            shift
            ;;
        -n|--no-save)
            NO_SAVE=true
            shift
            ;;
        -f|--csv-file)
            CSV_FILE="$2"
            shift 2
            ;;
        -L|--local-only)
            LOCAL_ONLY=true
            shift
            ;;
        -d|--storage-dir)
            LOCAL_STORAGE_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Input directory is required${NC}"
    show_help
    exit 1
fi

if [ ! -d "$INPUT_DIR" ]; then
    echo -e "${RED}Error: Input directory does not exist: $INPUT_DIR${NC}"
    exit 1
fi

# Build command
CMD="python3 main.py --input \"$INPUT_DIR\" --pattern \"$PATTERN\""

if [ $LIMIT -gt 0 ]; then
    CMD="$CMD --limit $LIMIT"
fi

CMD="$CMD --chunk-size $CHUNK_SIZE --chunk-overlap $CHUNK_OVERLAP"

if [ ! -z "$MAX_CHUNKS" ]; then
    CMD="$CMD --max-chunks $MAX_CHUNKS"
fi

if [ "$SEQUENTIAL" = true ]; then
    CMD="$CMD --sequential"
fi

if [ "$WEBHOOK_PRODUCTION" = true ]; then
    CMD="$CMD --production"
fi

if [ "$NO_SAVE" = true ]; then
    CMD="$CMD --no-save"
fi

CMD="$CMD --csv-file \"$CSV_FILE\""

if [ "$LOCAL_ONLY" = true ]; then
    CMD="$CMD --local-only"
fi

CMD="$CMD --local-storage-dir \"$LOCAL_STORAGE_DIR\""

# Show command
echo -e "${YELLOW}Executing:${NC}"
echo -e "${BLUE}$CMD${NC}"
echo ""

# Execute command
eval $CMD
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Batch processing completed successfully${NC}"
    exit 0
else
    echo -e "${RED}Batch processing failed with exit code $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi 