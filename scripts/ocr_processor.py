#!/usr/bin/env python
"""
OCR Processor Script

This script extracts text from images using Tesseract OCR.
It processes images individually or in batches, and saves the extracted text
along with metadata to CSV files and optionally to a vector database.

Requirements:
- Tesseract OCR must be installed
- Pytesseract Python package must be installed (pip install pytesseract)
- Python Imaging Library (PIL) must be installed (pip install pillow)

Usage:
  python ocr_processor.py [options] <image_path>
  python ocr_processor.py [options] --batch <directory_path>

Options:
  --output-dir DIR     Directory to save OCR results (default: ocr_results)
  --csv-file FILE      CSV file to append results (default: ocr_results.csv)
  --db                 Store results in vector database
  --lang LANG          OCR language (default: eng)
  --confidence         Include confidence scores in output
  --preprocess         Apply image preprocessing to improve OCR
  --batch              Process all images in directory
  --recursive          Process all subdirectories when using --batch
  --format FORMAT      Output format: text, csv, json (default: text)
  --skip-existing      Skip files that have already been processed
"""

import os
import sys
import csv
import json
import argparse
import time
import hashlib
from pathlib import Path
from datetime import datetime
import traceback

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
except ImportError:
    print("Required packages are missing. Please install:")
    print("pip install pytesseract pillow")
    sys.exit(1)

# Check if Tesseract is installed
try:
    pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    print("Error: Tesseract OCR is not installed or not in PATH")
    print("Please install Tesseract OCR:")
    print("  Ubuntu/Debian: sudo apt install tesseract-ocr")
    print("  macOS: brew install tesseract")
    print("  Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki")
    sys.exit(1)

class OCRProcessor:
    """Class to handle OCR processing of images"""
    
    def __init__(self, options):
        self.options = options
        self.output_dir = Path(options.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create or verify CSV file
        self.csv_file = Path(options.csv_file)
        self.csv_header = ['timestamp', 'image_path', 'hash', 'lang', 'word_count', 
                          'confidence', 'processing_time', 'text']
        
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_header)
    
    def generate_file_hash(self, file_path):
        """Generate a hash for the image file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    
    def preprocess_image(self, image):
        """Apply preprocessing to improve OCR results"""
        # Convert to grayscale
        image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Apply threshold to make text more distinct
        # Convert to binary image (black and white only)
        threshold = 200
        return image.point(lambda p: p > threshold and 255)
    
    def is_already_processed(self, file_hash):
        """Check if an image with this hash has already been processed"""
        if not self.csv_file.exists():
            return False
            
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) > 2 and row[2] == file_hash:
                    return True
        return False
    
    def process_image(self, image_path):
        """Process a single image and extract text using OCR"""
        try:
            start_time = time.time()
            
            # Generate hash and check if already processed
            file_hash = self.generate_file_hash(image_path)
            if self.options.skip_existing and self.is_already_processed(file_hash):
                print(f"Skipping already processed image: {image_path}")
                return None, None
            
            # Open the image
            image = Image.open(image_path)
            
            # Preprocess if requested
            if self.options.preprocess:
                image = self.preprocess_image(image)
            
            # Perform OCR
            ocr_options = {
                'lang': self.options.lang,
            }
            
            if self.options.confidence:
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, **ocr_options)
                text = " ".join([word for word in ocr_data['text'] if word.strip()])
                confidence = sum(ocr_data['conf']) / len(ocr_data['conf']) if len(ocr_data['conf']) > 0 else 0
            else:
                text = pytesseract.image_to_string(image, **ocr_options)
                confidence = -1  # Not calculated
            
            processing_time = time.time() - start_time
            
            # Prepare result data
            word_count = len(text.split()) if text else 0
            result = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image_path': str(image_path),
                'hash': file_hash,
                'lang': self.options.lang,
                'word_count': word_count,
                'confidence': confidence,
                'processing_time': processing_time,
                'text': text
            }
            
            # Save to CSV
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([result[key] for key in self.csv_header])
            
            # Save text to output file
            output_file = self.output_dir / f"{Path(image_path).stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Save JSON metadata if format is json
            if self.options.format == 'json':
                json_file = self.output_dir / f"{Path(image_path).stem}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
            
            return result, output_file
        
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            traceback.print_exc()
            return None, None
    
    def process_batch(self, directory_path):
        """Process all images in a directory"""
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            print(f"Error: {directory_path} is not a valid directory")
            return
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif']
        images = []
        
        if self.options.recursive:
            for ext in image_extensions:
                images.extend(directory.glob(f"**/*{ext}"))
                images.extend(directory.glob(f"**/*{ext.upper()}"))
        else:
            for ext in image_extensions:
                images.extend(directory.glob(f"*{ext}"))
                images.extend(directory.glob(f"*{ext.upper()}"))
        
        total_images = len(images)
        print(f"Found {total_images} images to process")
        
        processed = 0
        skipped = 0
        errors = 0
        start_time = time.time()
        
        for i, image_path in enumerate(images, 1):
            print(f"Processing {i}/{total_images}: {image_path}")
            result, output_file = self.process_image(image_path)
            
            if result is None:
                if self.is_already_processed(self.generate_file_hash(image_path)):
                    skipped += 1
                else:
                    errors += 1
            else:
                processed += 1
            
            # Show progress every 10 images
            if i % 10 == 0 or i == total_images:
                elapsed = time.time() - start_time
                images_per_sec = i / elapsed if elapsed > 0 else 0
                print(f"Progress: {i}/{total_images} ({i/total_images*100:.1f}%) - "
                      f"{images_per_sec:.2f} images/sec")
        
        # Print summary
        elapsed = time.time() - start_time
        print("\nOCR Processing Summary:")
        print(f"Total images: {total_images}")
        print(f"Successfully processed: {processed}")
        print(f"Skipped (already processed): {skipped}")
        print(f"Errors: {errors}")
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Average speed: {total_images/elapsed:.2f} images/sec if elapsed > 0 else 'N/A'")
        print(f"Results saved to: {self.output_dir}")
        print(f"CSV data saved to: {self.csv_file}")

def main():
    parser = argparse.ArgumentParser(description='Extract text from images using OCR')
    
    parser.add_argument('path', help='Path to image file or directory (if --batch is used)')
    parser.add_argument('--output-dir', default='ocr_results', help='Directory to save OCR results')
    parser.add_argument('--csv-file', default='ocr_results.csv', help='CSV file to append results')
    parser.add_argument('--db', action='store_true', help='Store results in vector database')
    parser.add_argument('--lang', default='eng', help='OCR language')
    parser.add_argument('--confidence', action='store_true', help='Include confidence scores')
    parser.add_argument('--preprocess', action='store_true', help='Apply image preprocessing')
    parser.add_argument('--batch', action='store_true', help='Process all images in directory')
    parser.add_argument('--recursive', action='store_true', help='Process all subdirectories')
    parser.add_argument('--format', choices=['text', 'csv', 'json'], default='text', 
                      help='Output format: text, csv, json')
    parser.add_argument('--skip-existing', action='store_true', help='Skip already processed files')
    
    args = parser.parse_args()
    
    # Initialize OCR processor
    processor = OCRProcessor(args)
    
    # Process single image or batch
    if args.batch:
        processor.process_batch(args.path)
    else:
        if not os.path.isfile(args.path):
            print(f"Error: {args.path} is not a valid file")
            sys.exit(1)
        
        result, output_file = processor.process_image(args.path)
        
        if result:
            print(f"OCR completed successfully for {args.path}")
            print(f"Text written to {output_file}")
            
            if args.confidence:
                print(f"Confidence: {result['confidence']:.2f}%")
            
            print(f"Word count: {result['word_count']}")
            
            if args.format == 'text':
                print("\nExtracted Text:")
                print("=" * 50)
                print(result['text'])
                print("=" * 50)
        else:
            print(f"OCR processing failed for {args.path}")
            sys.exit(1)

if __name__ == "__main__":
    main() 