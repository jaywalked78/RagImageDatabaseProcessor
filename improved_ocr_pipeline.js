const Airtable = require('airtable');
require('dotenv').config();
const { execSync, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');
const execPromise = util.promisify(exec);

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

// OCR processing configurations
const BATCH_SIZE = 10; // Process 10 frames at a time (Airtable limit)
const RATE_LIMIT_DELAY = 300; // Sleep 300ms between API calls

// Helper function to wait/sleep
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Log with timestamp
function log(message) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${message}`);
}

// Get all folders sorted chronologically
async function getAllFolders(baseDir = '/home/jason/Videos/screenRecordings') {
  try {
    log(`Getting all folders in ${baseDir}...`);
    const { stdout } = await execPromise(`find "${baseDir}" -type d -name "screen_recording_*" | sort`);
    const folders = stdout.trim().split('\n').filter(Boolean);
    log(`Found ${folders.length} folders`);
    return folders;
  } catch (error) {
    log(`Error getting folders: ${error.message}`);
    throw error;
  }
}

// Get records from Airtable by folder and filter out those that already have OCRData
async function getRecordsWithoutOCR(folderPath) {
  return new Promise((resolve, reject) => {
    log(`Finding frames without OCR data in folder: ${folderPath}`);
    
    const records = [];
    const folderName = path.basename(folderPath);
    
    table.select({
      filterByFormula: `AND({FolderName} = '${folderName}', OR(NOT({OCRData}), {OCRData} = ""))`,
      sort: [{ field: 'FolderPath', direction: 'asc' }]
    }).eachPage(
      function page(pageRecords, fetchNextPage) {
        records.push(...pageRecords);
        fetchNextPage();
      },
      function done(err) {
        if (err) {
          log(`Error fetching records: ${err.message}`);
          reject(err);
          return;
        }
        log(`Found ${records.length} frames without OCR data in folder ${folderName}`);
        resolve(records);
      }
    );
  });
}

// Process a batch of frames
async function processBatch(frames, folderPath) {
  if (frames.length === 0) {
    log(`No frames to process in this batch`);
    return 0;
  }
  
  log(`Processing batch of ${frames.length} frames...`);
  
  // Create a temporary file with frame IDs to process
  const tempFile = `frame_ids_to_process_${Date.now()}.txt`;
  fs.writeFileSync(tempFile, frames.map(record => record.id).join('\n'));
  
  try {
    // Run OCR process on these specific frames - limit to 10 at a time (Airtable's limit)
    const command = `python process_frames_by_path.py --folder-path-pattern "${folderPath}/*.jpg" --batch-size 10 --specific-ids ${tempFile}`;
    log(`Running command: ${command}`);
    
    const { stdout, stderr } = await execPromise(command);
    let ocrSuccess = true;
    
    if (stderr && stderr.includes("error")) {
      log(`OCR Processing errors: ${stderr}`);
      ocrSuccess = false;
    } else {
      log(`OCR Processing output: ${stdout}`);
      if (stderr) {
        log(`OCR Processing logs: ${stderr}`);
      }
    }
    
    // Only run parse_ocr_data.js if OCR was successful
    if (ocrSuccess) {
      // Run parse_ocr_data.js to update Flagged field
      const parseCommand = `node parse_ocr_data.js 10 false`;
      log(`Running command: ${parseCommand}`);
      
      const { stdout: parseStdout, stderr: parseStderr } = await execPromise(parseCommand);
      log(`Parse OCR data output: ${parseStdout}`);
      
      if (parseStderr) {
        log(`Parse OCR data errors: ${parseStderr}`);
      }
    } else {
      log(`Skipping parse_ocr_data.js due to OCR errors`);
    }
    
    return frames.length;
  } catch (error) {
    log(`Error processing batch: ${error.message}`);
    throw error;
  } finally {
    // Clean up temp file
    if (fs.existsSync(tempFile)) {
      fs.unlinkSync(tempFile);
    }
  }
}

// Process all frames in a folder
async function processFolder(folderPath) {
  try {
    log(`Processing folder: ${folderPath}`);
    
    // Get records from Airtable without OCR data
    const records = await getRecordsWithoutOCR(folderPath);
    
    if (records.length === 0) {
      log(`No frames without OCR data in folder ${path.basename(folderPath)}, skipping`);
      return 0;
    }
    
    log(`Found ${records.length} frames without OCR data to process`);
    
    // Process in batches of BATCH_SIZE (10 for Airtable's limit)
    let processed = 0;
    for (let i = 0; i < records.length; i += BATCH_SIZE) {
      const batch = records.slice(i, i + BATCH_SIZE);
      log(`Processing batch ${Math.floor(i/BATCH_SIZE) + 1} of ${Math.ceil(records.length/BATCH_SIZE)} for folder ${path.basename(folderPath)}`);
      
      await processBatch(batch, folderPath);
      processed += batch.length;
      
      // Sleep between batches to avoid rate limits and system overload
      log(`Sleeping for ${RATE_LIMIT_DELAY*2}ms between batches...`);
      await sleep(RATE_LIMIT_DELAY * 2);
    }
    
    log(`Processed ${processed} frames in folder ${path.basename(folderPath)}`);
    return processed;
  } catch (error) {
    log(`Error processing folder ${folderPath}: ${error.message}`);
    throw error;
  }
}

// Main function to process all folders chronologically
async function processAllFolders() {
  try {
    log('Starting OCR pipeline to process all folders...');
    
    // Get all folders sorted chronologically
    const folders = await getAllFolders();
    
    let totalProcessed = 0;
    
    // Process each folder
    for (const folder of folders) {
      const processed = await processFolder(folder);
      totalProcessed += processed;
      
      // Sleep between folders to avoid system overload
      log(`Sleeping for ${RATE_LIMIT_DELAY * 5}ms between folders...`);
      await sleep(RATE_LIMIT_DELAY * 5);
    }
    
    log(`OCR pipeline completed. Total frames processed: ${totalProcessed}`);
  } catch (error) {
    log(`Error in OCR pipeline: ${error.message}`);
    process.exit(1);
  }
}

// Process a specific folder
async function processSpecificFolder(folderPath) {
  try {
    log(`Processing specific folder: ${folderPath}`);
    const processed = await processFolder(folderPath);
    log(`Specific folder processing completed. Total frames processed: ${processed}`);
  } catch (error) {
    log(`Error processing specific folder: ${error.message}`);
    process.exit(1);
  }
}

// Main execution
(async () => {
  // Get command line arguments
  const args = process.argv.slice(2);
  const folderArg = args.find(arg => arg.startsWith('--folder='));
  
  try {
    if (folderArg) {
      // Process specific folder
      const folderPath = folderArg.split('=')[1];
      await processSpecificFolder(folderPath);
    } else {
      // Process all folders
      await processAllFolders();
    }
  } catch (error) {
    log(`Fatal error: ${error.message}`);
    process.exit(1);
  }
})(); 