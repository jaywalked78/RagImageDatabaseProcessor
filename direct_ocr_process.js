const Airtable = require('airtable');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const util = require('util');
const exec = util.promisify(require('child_process').exec);
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

// Field names
const FOLDER_FIELD = 'FolderPath';
const FRAME_PATH_FIELD = 'FolderPath';
const OCR_DATA_FIELD = 'OCRData';
const FLAGGED_FIELD = 'Flagged';
const SENSITIVITY_CONCERNS_FIELD = 'SensitivityConcerns';

// Configure Tesseract path if needed
const TESSERACT_PATH = process.env.TESSERACT_PATH || 'tesseract';

// Initialize Airtable
const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

// Keywords for sensitive content detection
const SENSITIVE_KEYWORDS = [
  'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey', 'key', 
  'credential', 'auth', 'private', 'sensitive', 'confidential', 'restricted',
  'login', 'username', 'user', 'email', 'address', 'phone', 'ssn', 'social security',
  'credit', 'card', 'visa', 'mastercard', 'amex', 'cvv', 'cvv2', 'cvc', 'pin',
  'bank', 'account', 'routing', 'invoice', 'license', 'certificate', 'password:',
  'pwd:', 'api_key:', 'apikey:', 'secret:', 'token:'
];

/**
 * Perform OCR on an image file
 * @param {string} imagePath - Path to the image file
 * @returns {Promise<string>} - OCR text
 */
async function performOCR(imagePath) {
  try {
    console.log(`Performing OCR on ${imagePath}`);
    const outputBase = `${path.dirname(imagePath)}/${path.basename(imagePath, path.extname(imagePath))}`;
    
    const cmd = `${TESSERACT_PATH} "${imagePath}" stdout -l eng --oem 1 --psm 3`;
    const { stdout, stderr } = await exec(cmd);
    
    if (stderr) {
      console.warn(`OCR Warning: ${stderr}`);
    }
    
    return stdout;
  } catch (error) {
    console.error(`OCR Error for ${imagePath}: ${error.message}`);
    return '';
  }
}

/**
 * Check if OCR text contains sensitive information
 * @param {string} ocrText - OCR text to analyze
 * @returns {Object} - Object with sensitivity info
 */
function checkForSensitiveInfo(ocrText) {
  if (!ocrText) return { sensitive: false, types: [] };
  
  const lowerText = ocrText.toLowerCase();
  const foundKeywords = [];
  
  // Check for sensitive keywords
  for (const keyword of SENSITIVE_KEYWORDS) {
    if (lowerText.includes(keyword)) {
      foundKeywords.push(keyword);
    }
  }
  
  // Look for patterns that might be sensitive
  const patterns = {
    'credit_card': /\b(?:\d[ -]*?){13,16}\b/g, // Credit card numbers
    'api_key': /\b[a-zA-Z0-9_-]{20,40}\b/g, // API keys/tokens
    'email': /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, // Email addresses
    'ip_address': /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, // IP addresses
    'phone_number': /\b(?:\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b/g, // Phone numbers
    'aws_key': /\b(AKIA[0-9A-Z]{16})\b/g, // AWS Access Keys
    'password_fields': /\b(password|passwd|pwd)[\s]*[=:].+/g // Password assignments
  };
  
  const patternMatches = [];
  for (const [type, pattern] of Object.entries(patterns)) {
    if (pattern.test(lowerText)) {
      patternMatches.push(type);
    }
  }
  
  return {
    sensitive: foundKeywords.length > 0 || patternMatches.length > 0,
    types: [...new Set([...foundKeywords, ...patternMatches])]
  };
}

/**
 * Process a batch of records
 * @param {Array} records - Array of Airtable records
 */
async function processRecords(records) {
  const updates = [];
  
  for (const record of records) {
    try {
      const imagePath = record.get(FOLDER_FIELD);
      
      if (!imagePath) {
        console.log(`Record ${record.id}: No image path found, skipping`);
        continue;
      }
      
      // Check if image file exists before attempting OCR
      if (!fs.existsSync(imagePath)) {
        console.log(`Record ${record.id}: Image file does not exist at path: ${imagePath}, skipping`);
        continue;
      }
      
      // Perform OCR
      const ocrText = await performOCR(imagePath);
      
      // Check for sensitive info
      const sensitivityAnalysis = checkForSensitiveInfo(ocrText);
      
      // Format the Flagged field value as simple true/false
      let flaggedValue = sensitivityAnalysis.sensitive ? "true" : "false";
      
      // Create sensitivity concerns details when sensitive content is found
      let sensitivityConcerns = "";
      if (sensitivityAnalysis.sensitive) {
        sensitivityConcerns = `Sensitive content detected: ${sensitivityAnalysis.types.join(', ')}`;
        console.log(`Record ${record.id}: SENSITIVE CONTENT DETECTED - ${sensitivityAnalysis.types.join(', ')}`);
      }
      
      // Add to updates
      const updateFields = {
        [OCR_DATA_FIELD]: ocrText,
        [FLAGGED_FIELD]: flaggedValue
      };
      
      // Only include sensitivity concerns if there are any
      if (sensitivityConcerns) {
        updateFields[SENSITIVITY_CONCERNS_FIELD] = sensitivityConcerns;
      }
      
      updates.push({
        id: record.id,
        fields: updateFields
      });
      
      console.log(`Record ${record.id}: OCR completed, flagged=${flaggedValue}${sensitivityConcerns ? ', concerns recorded' : ''}`);
    } catch (error) {
      console.error(`Error processing record ${record.id}:`, error);
    }
  }
  
  // Perform batch update
  if (updates.length > 0) {
    try {
      // Process in batches of 10
      for (let i = 0; i < updates.length; i += 10) {
        const batch = updates.slice(i, i + 10);
        await table.update(batch);
        console.log(`✓ Updated ${batch.length} records (batch ${Math.floor(i/10) + 1})`);
      }
    } catch (error) {
      console.error('Error updating batch:', error);
      
      // Try individually
      for (const update of updates) {
        try {
          await table.update([update]);
          console.log(`✓ Updated record ${update.id} individually`);
        } catch (err) {
          console.error(`Failed to update record ${update.id}:`, err);
        }
      }
    }
  }
}

/**
 * Main function
 * @param {number} batchSize - Number of records to process at once
 * @param {string} specificFolder - Optional specific folder to process
 * @param {string} pageToken - Page token for pagination (default: null)
 */
async function main(batchSize = 10, specificFolder = null, pageToken = null) {
  console.log(`Starting direct OCR processing with batch size ${batchSize}${pageToken ? ', with pagination token' : ', first batch'}`);
  
  try {
    // Set up filter for specific folder if provided
    let filterFormula = '';
    if (specificFolder) {
      console.log(`Processing only records from folder: ${specificFolder}`);
      // Construct filter formula to match folder path pattern
      filterFormula = `FIND("${specificFolder}/", {FolderPath}) = 1`;
    }
    
    console.log('Fetching records from Airtable...');
    
    // Fetch records with filter if applicable
    const query = {
      pageSize: batchSize
    };
    
    // Add filter formula if provided
    if (filterFormula) {
      query.filterByFormula = filterFormula;
    }
    
    // Add offset token if provided (for pagination)
    if (pageToken && pageToken !== 'null' && pageToken !== 'undefined') {
      query.offset = pageToken;
    }
    
    // Fetch records
    const page = await table.select(query).firstPage();
    
    console.log(`Processing ${page.length} records`);
    
    // Get the next page token if available
    const nextPageToken = page._pagination ? page._pagination.offset : null;
    if (nextPageToken) {
      console.log(`Next page token available: ${nextPageToken.substring(0, 20)}...`);
    } else {
      console.log('No more pages available');
    }
    
    // Process the current page of records
    await processRecords(page);
    
    // Output the next page token for the shell script to capture
    console.log(`NEXT_PAGE_TOKEN:${nextPageToken || ''}`);
    
    console.log('OCR processing completed successfully!');
    
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

// If running as script
if (require.main === module) {
  const batchSize = process.argv[2] ? parseInt(process.argv[2]) : 10;
  const specificFolder = process.argv[3] || null;
  const pageToken = process.argv[4] || null;
  
  main(batchSize, specificFolder, pageToken)
    .then(() => {
      console.log('Script completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('Script failed:', error);
      process.exit(1);
    });
}

module.exports = { performOCR, checkForSensitiveInfo, main }; 