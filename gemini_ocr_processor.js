const Airtable = require('airtable');
const fs = require('fs');
const path = require('path');
const { execSync, exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

// Field names
const FOLDER_FIELD = 'FolderPath';
const OCR_DATA_FIELD = 'OCRData';
const FLAGGED_FIELD = 'Flagged';
const SENSITIVITY_CONCERNS_FIELD = 'SensitivityConcerns';

// Configure Tesseract path if needed
const TESSERACT_PATH = process.env.TESSERACT_PATH || 'tesseract';

// Configure Gemini
const GEMINI_API_KEY = process.env.GEMINI_API_KEY_1 || process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-1.5-flash';

// Initialize APIs
const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

/**
 * Perform OCR on an image file
 * @param {string} imagePath - Path to the image file
 * @returns {Promise<string>} - OCR text
 */
async function performOCR(imagePath) {
  try {
    console.log(`Performing OCR on ${imagePath}`);
    
    const cmd = `${TESSERACT_PATH} "${imagePath}" stdout -l eng --oem 1 --psm 3`;
    const { stdout, stderr } = await execAsync(cmd);
    
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
 * Analyze OCR text with Google Gemini
 * @param {string} ocrText - Raw OCR text to analyze
 * @param {string} imagePath - Path to the original image (for context)
 * @returns {Promise<Object>} - Analysis results
 */
async function analyzeWithGemini(ocrText, imagePath) {
  try {
    console.log(`Analyzing OCR text with Gemini: ${ocrText.substring(0, 50)}${ocrText.length > 50 ? '...' : ''}`);
    
    // Create Gemini model
    const model = genAI.getGenerativeModel({ model: GEMINI_MODEL });
    
    // Prepare the prompt
    const prompt = `
      You are analyzing OCR text extracted from a screen recording frame.
      Image path: ${imagePath}
      
      OCR TEXT:
      ${ocrText}
      
      Please analyze this text and provide the following:
      1. Extract and clean up ONLY meaningful text from the OCR output.
         - Remove any garbled text, OCR errors, or nonsensical content
         - Focus on keeping text that forms coherent phrases
      
      2. Detect if there is any sensitive information such as:
         - Passwords, usernames, login credentials
         - API keys, tokens, secrets
         - Private data, personally identifiable information
         - Credit card numbers, financial information
         - Authentication information, JWT tokens
         - Environment variables, configuration settings
         - Private URLs, SSH keys, or certificates
      
      3. List ALL types of sensitive information found with specific examples.
      
      Format your response as a JSON object with this exact schema:
      {
        "cleanedText": "Cleaned and meaningful text from OCR",
        "containsSensitiveInfo": true/false,
        "sensitiveContentTypes": ["list", "of", "types"],
        "sensitivityDetails": "Detailed explanation of sensitive content found"
      }
      
      Respond ONLY with the JSON object - no introduction, explanation, or markdown.
    `;
    
    // Call Gemini API
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    
    // Extract the JSON from the response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.error("Failed to extract JSON from Gemini response");
      return {
        cleanedText: ocrText,
        containsSensitiveInfo: false,
        sensitiveContentTypes: [],
        sensitivityDetails: "Error: Could not parse Gemini response"
      };
    }
    
    const analysis = JSON.parse(jsonMatch[0]);
    
    // Ensure all expected fields exist
    return {
      cleanedText: analysis.cleanedText || ocrText,
      containsSensitiveInfo: analysis.containsSensitiveInfo || false,
      sensitiveContentTypes: analysis.sensitiveContentTypes || [],
      sensitivityDetails: analysis.sensitivityDetails || ""
    };
  } catch (error) {
    console.error(`Gemini analysis error: ${error.message}`);
    // Fallback to simpler analysis if Gemini fails
    return {
      cleanedText: ocrText,
      containsSensitiveInfo: false,
      sensitiveContentTypes: [],
      sensitivityDetails: `Error during analysis: ${error.message}`
    };
  }
}

/**
 * Process a batch of records
 * @param {Array} records - Array of Airtable records
 */
async function processRecords(records) {
  const updates = [];
  let processedCount = 0;
  
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
      
      if (!ocrText.trim()) {
        console.log(`Record ${record.id}: No OCR text extracted, setting empty data`);
        updates.push({
          id: record.id,
          fields: {
            [OCR_DATA_FIELD]: "No readable text",
            [FLAGGED_FIELD]: "false",
            [SENSITIVITY_CONCERNS_FIELD]: ""
          }
        });
        continue;
      }
      
      // Analyze with Gemini
      const analysis = await analyzeWithGemini(ocrText, imagePath);
      
      // Prepare Airtable update
      const updateFields = {
        [OCR_DATA_FIELD]: analysis.cleanedText || ocrText,
        [FLAGGED_FIELD]: analysis.containsSensitiveInfo ? "true" : "false"
      };
      
      // Add sensitivity concerns if sensitive content was found
      if (analysis.containsSensitiveInfo && analysis.sensitiveContentTypes.length > 0) {
        updateFields[SENSITIVITY_CONCERNS_FIELD] = `Sensitive content detected: ${analysis.sensitiveContentTypes.join(', ')}. ${analysis.sensitivityDetails}`;
        console.log(`Record ${record.id}: SENSITIVE CONTENT DETECTED - ${analysis.sensitiveContentTypes.join(', ')}`);
      }
      
      updates.push({
        id: record.id,
        fields: updateFields
      });
      
      console.log(`Record ${record.id}: OCR and analysis completed`);
      processedCount++;
      
      // Add a small delay between records to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error(`Error processing record ${record.id}:`, error);
    }
  }
  
  // Perform batch update if we have any updates
  if (updates.length > 0) {
    try {
      // Process in batches of 10 (Airtable's limit)
      for (let i = 0; i < updates.length; i += 10) {
        const batch = updates.slice(i, i + 10);
        await table.update(batch);
        console.log(`✓ Updated ${batch.length} records successfully (batch ${Math.floor(i/10) + 1})`);
      }
    } catch (error) {
      console.error('Error updating batch:', error);
      
      // Try individually if batch update fails
      for (const update of updates) {
        try {
          await table.update([update]);
          console.log(`✓ Updated record ${update.id} individually`);
        } catch (recordError) {
          console.error(`Failed to update record ${update.id}:`, recordError);
        }
      }
    }
  }
  
  console.log(`Processed ${processedCount} records with Gemini OCR analysis`);
  return { processed: processedCount, updated: updates.length };
}

/**
 * Main function
 * @param {number} batchSize - Number of records to process at once
 * @param {string} specificFolder - Optional specific folder to process
 * @param {string} pageToken - Page token for pagination
 */
async function main(batchSize = 10, specificFolder = null, pageToken = null) {
  console.log(`Starting Gemini OCR processing with batch size ${batchSize}${pageToken ? ', with pagination token' : ', first batch'}`);
  
  try {
    // Set up filter for specific folder if provided
    let filterFormula = '';
    if (specificFolder) {
      console.log(`Processing only records from folder: ${specificFolder}`);
      // Construct filter formula to match folder path pattern
      filterFormula = `FIND("${specificFolder}/", {${FOLDER_FIELD}}) = 1`;
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
    const result = await processRecords(page);
    
    // Output the next page token for the shell script to capture
    console.log(`NEXT_PAGE_TOKEN:${nextPageToken || ''}`);
    
    console.log(`OCR processing completed successfully! Processed ${result.processed} records, updated ${result.updated} records.`);
    
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

module.exports = { performOCR, analyzeWithGemini, main }; 