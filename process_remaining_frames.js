#!/usr/bin/env node

/**
 * Script to process all remaining frames in screen recording folders
 * 
 * This script will:
 * 1. Sort folders in chronological order
 * 2. Exclude folders already marked as finished in Airtable
 * 3. Generate a list of frames from remaining folders
 * 4. Process them using the robust OCR worker
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const { promisify } = require('util');
const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);
const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);
require('dotenv').config();

// Set variables
const BASE_DIR = '/home/jason/Videos/screenRecordings';
const TEMP_DIR = '/tmp/database_tokenizer';  // Hardcoded absolute path
const LOG_DIR = '/home/jason/Documents/DatabaseAdvancedTokenizer/logs';  // Hardcoded absolute path
const WORKER_ID = 1;

// Create directories if they don't exist
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
  log(`Created temp directory: ${TEMP_DIR}`);
}
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
  log(`Created logs directory: ${LOG_DIR}`);
}

// Generate timestamp for this run
const TIMESTAMP = new Date().toISOString().replace(/[:.]/g, '').replace('T', '_').substring(0, 15);
const LOG_FILE = path.join(LOG_DIR, `process_all_frames_${TIMESTAMP}.log`);

// Log function
function log(message) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const logMessage = `[${timestamp}] ${message}`;
  console.log(logMessage);
  fs.appendFileSync(LOG_FILE, logMessage + '\n');
}

// Validate configuration
function validateConfig() {
  log('Starting to process all remaining frames');
  log(`Base directory: ${BASE_DIR}`);
  log(`Temp directory: ${TEMP_DIR}`);
  log(`Log directory: ${LOG_DIR}`);
  
  if (!process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN) {
    log('Error: AIRTABLE_PERSONAL_ACCESS_TOKEN not set in .env file');
    process.exit(1);
  }
  
  if (!process.env.AIRTABLE_BASE_ID) {
    log('Error: AIRTABLE_BASE_ID not set in .env file');
    process.exit(1);
  }
  
  const trackingTable = process.env.AIRTABLE_TRACKING_TABLE || 'Finished OCR Processed Folders';
  const folderNameField = process.env.FOLDER_NAME_FIELD || 'FolderName';
  
  return { trackingTable, folderNameField };
}

// Fetch finished folders from Airtable
async function fetchFinishedFolders(trackingTable, folderNameField) {
  log(`Fetching list of finished folders from Airtable table: ${trackingTable}`);
  
  const AIRTABLE_RESPONSE_FILE = path.join(TEMP_DIR, `airtable_response_${TIMESTAMP}.json`);
  const FINISHED_FOLDERS_FILE = path.join(TEMP_DIR, `finished_folders_${TIMESTAMP}.txt`);
  
  try {
    // Ensure the temp directory exists
    if (!fs.existsSync(TEMP_DIR)) {
      fs.mkdirSync(TEMP_DIR, { recursive: true });
      log(`Created temp directory: ${TEMP_DIR}`);
    }
    
    // Execute the curl command and capture the raw response
    const curl = `curl -s -X GET "https://api.airtable.com/v0/${process.env.AIRTABLE_BASE_ID}/${trackingTable}?fields%5B%5D=${folderNameField}" -H "Authorization: Bearer ${process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN}" -H "Content-Type: application/json"`;
    log(`Executing curl command: ${curl.substring(0, 100)}...`);
    const result = execSync(curl);
    
    // Log the response size and save to file
    const responseSize = result.length;
    log(`Received Airtable response: ${responseSize} bytes`);
    fs.writeFileSync(AIRTABLE_RESPONSE_FILE, result);
    log(`Saved Airtable response to: ${AIRTABLE_RESPONSE_FILE}`);
    
    // Parse the response with extra error handling
    let finishedFolders = [];
    try {
      // Check if response is empty
      if (!result || responseSize === 0) {
        log('WARNING: Received empty response from Airtable');
        fs.writeFileSync(FINISHED_FOLDERS_FILE, '');
        return [];
      }
      
      // Print the first 200 characters of the response for debugging
      const responsePreview = result.toString().substring(0, 200).replace(/\n/g, '');
      log(`Response preview: ${responsePreview}...`);
      
      // Try to parse JSON
      const response = JSON.parse(result.toString());
      log(`Successfully parsed JSON response`);
      
      // Extract folder names
      if (response.records && Array.isArray(response.records)) {
        log(`Found ${response.records.length} records in response`);
        
        finishedFolders = response.records
          .filter(record => record.fields && record.fields[folderNameField])
          .map(record => record.fields[folderNameField]);
          
        log(`Extracted ${finishedFolders.length} folder names`);
      } else {
        log(`WARNING: Response does not contain expected 'records' array. Structure: ${JSON.stringify(Object.keys(response))}`);
      }
    } catch (parseError) {
      log(`ERROR parsing Airtable response: ${parseError.message}`);
      log(`Response content (first 500 chars): ${result.toString().substring(0, 500)}`);
      
      // Attempt to manually parse if JSON parsing fails
      log(`Attempting manual extraction with regex...`);
      const folderPattern = new RegExp(`"${folderNameField}":"([^"]*)"`, 'g');
      let match;
      while ((match = folderPattern.exec(result.toString())) !== null) {
        finishedFolders.push(match[1]);
      }
      log(`Manually extracted ${finishedFolders.length} folder names`);
    }
    
    // Write the folder names to a file
    fs.writeFileSync(FINISHED_FOLDERS_FILE, finishedFolders.join('\n'));
    log(`Found ${finishedFolders.length} finished folders in Airtable`);
    log(`Saved folder names to: ${FINISHED_FOLDERS_FILE}`);
    return finishedFolders;
    
  } catch (error) {
    log(`ERROR fetching finished folders: ${error.message}`);
    if (error.stderr) {
      log(`STDERR: ${error.stderr.toString()}`);
    }
    // Create empty finished folders file to avoid further errors
    fs.writeFileSync(FINISHED_FOLDERS_FILE, '');
    return [];
  }
}

// Get all folders sorted chronologically
async function getAllFolders() {
  log('Getting all folders in chronological order...');
  
  try {
    // Get all directories in BASE_DIR
    const items = await readdir(BASE_DIR);
    let folders = [];
    
    for (const item of items) {
      const fullPath = path.join(BASE_DIR, item);
      const stats = await stat(fullPath);
      
      if (stats.isDirectory() && item.startsWith('screen_recording_')) {
        folders.push({ path: fullPath, name: item });
      }
    }
    
    // Sort chronologically based on folder name
    folders.sort((a, b) => {
      const partsA = a.name.split('_');
      const partsB = b.name.split('_');
      
      // Compare year, month, day
      const dateA = partsA[2];
      const dateB = partsB[2];
      if (dateA !== dateB) return dateA.localeCompare(dateB);
      
      // Compare hour, minute, second
      const timeA = `${partsA[4]}_${partsA[5]}_${partsA[6]}`;
      const timeB = `${partsB[4]}_${partsB[5]}_${partsB[6]}`;
      return timeA.localeCompare(timeB);
    });
    
    log(`Found ${folders.length} total folders`);
    return folders;
    
  } catch (error) {
    log(`Error getting folders: ${error.message}`);
    return [];
  }
}

// Filter out finished folders
function filterFolders(allFolders, finishedFolders) {
  log('Filtering out finished folders...');
  
  const remainingFolders = allFolders.filter(folder => 
    !finishedFolders.includes(folder.name)
  );
  
  log(`After filtering, ${remainingFolders.length} folders need processing (skipping ${allFolders.length - remainingFolders.length} folders)`);
  return remainingFolders;
}

// Collect frames from folders
async function collectFrames(folders) {
  log('Collecting frames from folders...');
  const REMAINING_FRAMES_FILE = path.join(TEMP_DIR, `remaining_frames_${TIMESTAMP}.txt`);
  
  let totalFrames = 0;
  let folderCount = 0;
  let framesList = [];
  
  for (const folder of folders) {
    folderCount++;
    log(`Processing folder ${folderCount}/${folders.length}: ${folder.name}`);
    
    try {
      // Find frames recursively in this folder
      const findCmd = `find "${folder.path}" -type f -name "*.jpg"`;
      const frames = execSync(findCmd).toString().trim().split('\n');
      
      // Filter out empty strings
      const validFrames = frames.filter(frame => frame.trim() !== '');
      
      // Sort frames
      validFrames.sort();
      
      if (validFrames.length > 0) {
        totalFrames += validFrames.length;
        framesList = framesList.concat(validFrames);
        log(`Added ${validFrames.length} frames from folder: ${folder.name}`);
      } else {
        log(`No frames found in folder: ${folder.name}`);
      }
      
    } catch (error) {
      log(`Error processing folder ${folder.name}: ${error.message}`);
    }
  }
  
  // Write all frames to file
  await writeFileAsync(REMAINING_FRAMES_FILE, framesList.join('\n'));
  log(`Collected ${totalFrames} frames from ${folders.length} folders`);
  
  return { framesFile: REMAINING_FRAMES_FILE, totalFrames };
}

// Run the worker
async function runWorker(framesFile, totalFrames) {
  log(`Starting to process ${totalFrames} frames using worker`);
  log(`Using worker ID: ${WORKER_ID}`);
  log(`Using frames file: ${framesFile}`);
  
  return new Promise((resolve, reject) => {
    const worker = spawn('./run_with_logs.sh', [WORKER_ID.toString(), framesFile], {
      stdio: 'inherit',
      shell: true
    });
    
    worker.on('close', (code) => {
      if (code === 0) {
        log('Worker completed successfully');
        resolve();
      } else {
        log(`Worker exited with code ${code}`);
        reject(new Error(`Worker exited with code ${code}`));
      }
    });
    
    worker.on('error', (err) => {
      log(`Failed to start worker: ${err.message}`);
      reject(err);
    });
  });
}

// Main function
async function main() {
  try {
    const { trackingTable, folderNameField } = validateConfig();
    const finishedFolders = await fetchFinishedFolders(trackingTable, folderNameField);
    const allFolders = await getAllFolders();
    
    if (allFolders.length === 0) {
      log('Error: No folders found matching pattern "screen_recording_*"');
      return;
    }
    
    const remainingFolders = filterFolders(allFolders, finishedFolders);
    
    if (remainingFolders.length === 0) {
      log('No folders left to process! All folders appear to be finished.');
      return;
    }
    
    const { framesFile, totalFrames } = await collectFrames(remainingFolders);
    
    if (totalFrames === 0) {
      log('No frames found in the remaining folders!');
      return;
    }
    
    await runWorker(framesFile, totalFrames);
    
    log('Finished processing frames');
    log('Check the worker log for detailed results');
    
  } catch (error) {
    log(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Run the main function
main(); 