const Airtable = require('airtable');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

// Field names in Airtable
const OCR_DATA_FIELD = 'OCRData';
const FLAGGED_FIELD = 'Flagged';

// Main function to process OCR data
async function processOCRData(batchSize = 10, onlyUnprocessed = false) {
  // Limit batch size to 10 due to Airtable's maximum records per request
  if (batchSize > 10) {
    console.log(`Warning: Airtable has a limit of 10 records per update. Reducing batch size from ${batchSize} to 10.`);
    batchSize = 10;
  }

  console.log(`Starting OCR data processing (batch size: ${batchSize}, only unprocessed: ${onlyUnprocessed})...`);
  
  // Default is to process all records without checking for OCR data
  let filterFormula = "";
  
  // If only processing records that haven't been parsed yet
  if (onlyUnprocessed) {
    // Look for records that have not been flagged yet
    filterFormula = `{${FLAGGED_FIELD}} = ""`;
    console.log(`Looking for records that need flagging: ${filterFormula}`);
  } else {
    console.log('Processing ALL records in the table chronologically');
  }
  
  // Fetch records based on filter
  const selectOptions = {
    sort: [{ field: 'FrameID', direction: 'asc' }]
  };
  
  // Only add filterByFormula if we have a filter
  if (filterFormula) {
    selectOptions.filterByFormula = filterFormula;
  }
  
  // Fetch records based on filter
  const records = await table.select(selectOptions).all();
  
  console.log(`Found ${records.length} records`);
  
  // Add diagnostic output for the first record if available
  if (records.length > 0) {
    const sampleRecord = records[0];
    const sampleOCRData = sampleRecord.get(OCR_DATA_FIELD);
    console.log('Sample OCRData field value:');
    console.log(sampleOCRData ? sampleOCRData.substring(0, 200) + '...' : 'Empty');
    
    // Check if it appears to be JSON
    if (sampleOCRData && sampleOCRData.startsWith('{') && sampleOCRData.includes('ocr_text')) {
      console.log('Sample appears to be JSON structure - will extract ocr_text value');
    } else {
      console.log('Sample does not appear to be in JSON format');
    }
  }
  
  // Process records in batches
  for (let i = 0; i < records.length; i += batchSize) {
    const batch = records.slice(i, i + batchSize);
    console.log(`Processing batch ${Math.floor(i/batchSize) + 1} (${batch.length} records)...`);
    
    // Prepare batch updates
    const updates = [];
    
    // Process each record in the batch
    for (const record of batch) {
      try {
        const recordId = record.id;
        const ocrDataString = record.get(OCR_DATA_FIELD);
        
        // Handle records with no OCR data but still update flags
        if (!ocrDataString) {
          console.log(`Record ${recordId}: No OCR data found`);
          
          // Even if no OCR data, ensure the Flagged field is set appropriately
          updates.push({
            id: recordId,
            fields: {
              [FLAGGED_FIELD]: "false", // No OCR data means no sensitive info
              [OCR_DATA_FIELD]: "" // Ensure a consistent empty string
            }
          });
          continue;
        }
        
        // With the updated Python script, OCRData now contains the direct text
        // No JSON parsing is needed for new records
        let ocrText = ocrDataString || '';
        
        // For backward compatibility, check if this might be a JSON string (legacy format)
        let containsSensitiveInfo = false;
        let sensitiveContentTypes = [];
        
        if (ocrText.startsWith('{') && ocrText.includes('"ocr_text"')) {
          console.log(`Record ${recordId}: Legacy JSON format detected, extracting data`);
          
          try {
            // This appears to be an old format JSON string
            const legacyData = JSON.parse(ocrText);
            ocrText = legacyData.ocr_text || '';
            containsSensitiveInfo = !!legacyData.contains_sensitive_info;
            
            // Enhanced handling of sensitive content types from legacy format
            if (legacyData.sensitive_content_types) {
              if (Array.isArray(legacyData.sensitive_content_types)) {
                sensitiveContentTypes = legacyData.sensitive_content_types;
              } else if (typeof legacyData.sensitive_content_types === 'string') {
                // Handle case where sensitive_content_types might be a comma-separated string
                sensitiveContentTypes = legacyData.sensitive_content_types.split(',').map(type => type.trim());
              } else if (typeof legacyData.sensitive_content_types === 'object') {
                // Handle case where it might be an object with keys as types
                sensitiveContentTypes = Object.keys(legacyData.sensitive_content_types);
              }
            }
            
            // Check additional fields that might indicate sensitive content
            if (legacyData.sensitive_info_details) {
              const details = legacyData.sensitive_info_details;
              
              // Add specific categories if they have positive counts
              if (details.api_keys > 0) sensitiveContentTypes.push('api_keys');
              if (details.passwords > 0) sensitiveContentTypes.push('passwords');
              if (details.card_numbers > 0) sensitiveContentTypes.push('payment_card_data');
              if (details.env_variables > 0) sensitiveContentTypes.push('environment_variables');
            }
          } catch (jsonError) {
            console.error(`Error parsing legacy JSON for record ${recordId}:`, jsonError);
            // Keep the original text, but check for sensitive info flags
            const sensitiveMatch = ocrText.match(/"contains_sensitive_info"\s*:\s*(true|false)/);
            containsSensitiveInfo = sensitiveMatch ? (sensitiveMatch[1] === "true") : false;
            
            // Try to extract sensitive content types even if JSON parsing failed
            const typesMatch = ocrText.match(/"sensitive_content_types"\s*:\s*\[(.*?)\]/);
            if (typesMatch && typesMatch[1]) {
              // This regex extracts strings from array format like ["type1", "type2"]
              const typeRegex = /"([^"]*)"/g;
              let match;
              while ((match = typeRegex.exec(typesMatch[1])) !== null) {
                sensitiveContentTypes.push(match[1]);
              }
            }
          }
        } else {
          // For direct text format, we don't know if it's sensitive
          // Enhanced detection with more specific patterns
          
          // Define regex patterns for different types of sensitive information
          const patterns = {
            api_keys: [
              /api[_\s]?key[=:]\s*[A-Za-z0-9_\-]{20,}/i,
              /token[=:]\s*[A-Za-z0-9_\-]{20,}/i,
              /secret[=:]\s*[A-Za-z0-9_\-]{20,}/i
            ],
            passwords: [
              /password[=:]\s*[^\s]+/i,
              /pwd[=:]\s*[^\s]+/i,
              /passwd[=:]\s*[^\s]+/i
            ],
            payment_card_data: [
              /(?<!\d)(?:\d{4}[\s\-]?){3}\d{4}(?!\d)/,  // Credit card pattern
              /cvv[=:]\s*\d{3,4}/i,
              /expir(y|ation)[=:]\s*\d{1,2}\/\d{2,4}/i
            ],
            environment_variables: [
              /(?:DATABASE|DB)_URL[=:]/i,
              /(?:MONGO|POSTGRES|SQL).*[=:]/i,
              /CONNECTION_STRING[=:]/i
            ]
          };
          
          // Test each pattern category and add the type if found
          for (const [type, typePatterns] of Object.entries(patterns)) {
            for (const pattern of typePatterns) {
              if (pattern.test(ocrText)) {
                sensitiveContentTypes.push(type);
                containsSensitiveInfo = true;
                break; // Only add each type once
              }
            }
          }
          
          // If we've detected sensitive info but no specific types, mark as auto-detected
          if (containsSensitiveInfo && sensitiveContentTypes.length === 0) {
            sensitiveContentTypes = ['auto_detected'];
          } else if (!containsSensitiveInfo) {
            // Fallback to basic detection if nothing found by patterns
            containsSensitiveInfo = /password|api.?key|token|secret|credit.?card|ssn|social.?security/i.test(ocrText);
            
            if (containsSensitiveInfo) {
              sensitiveContentTypes = ['auto_detected'];
            }
          }
        }
        
        console.log(`Record ${recordId}: OCR Text = ${ocrText.substring(0, 50)}${ocrText.length > 50 ? '...' : ''}`);
        console.log(`Record ${recordId}: Contains sensitive info = ${containsSensitiveInfo}`);
        
        // Add detailed logging for sensitive content types
        if (sensitiveContentTypes.length > 0) {
          console.log(`Record ${recordId}: Detected sensitive content types: ${JSON.stringify(sensitiveContentTypes)}`);
        }
        
        // Format the Flagged field value according to requirements
        let flaggedValue;
        if (!containsSensitiveInfo) {
          flaggedValue = "false";
        } else {
          // If sensitive, include the sensitive types in parentheses
          if (sensitiveContentTypes.length > 0) {
            // Clean up the sensitive content types to ensure they're properly formatted
            const cleanedTypes = sensitiveContentTypes.map(type => {
              // Remove any quotes, brackets, extra spaces
              const cleanedType = type.toString().replace(/["'\[\]{}]/g, '').trim();
              
              // Normalize common sensitive content type names to match Python categories
              switch(cleanedType.toLowerCase()) {
                case 'api_key':
                case 'apikey':
                case 'api key':
                  return 'api_keys';
                case 'password':
                case 'passwd':
                case 'pwd':
                  return 'passwords';
                case 'card':
                case 'credit_card':
                case 'creditcard':
                case 'card_number':
                  return 'payment_card_data';
                case 'env':
                case 'environment':
                case 'env_var':
                  return 'environment_variables';
                case 'auto_detected':
                case 'autodetected':
                  return 'auto_detected';
                default:
                  return cleanedType;
              }
            }).filter(type => type); // Remove any empty strings
            
            // Deduplicate types to avoid repetition
            const uniqueTypes = [...new Set(cleanedTypes)];
            
            if (uniqueTypes.length > 0) {
              flaggedValue = `true (sensitive_content_types: ${uniqueTypes.join(', ')})`;
              // Ensure we're logging the full flagged value with content types
              console.log(`Record ${recordId}: Setting Flagged to "${flaggedValue}"`);
            } else {
              flaggedValue = "true";
              console.log(`Record ${recordId}: Setting Flagged to "true" (no specific types identified)`);
            }
          } else {
            flaggedValue = "true";
            console.log(`Record ${recordId}: Setting Flagged to "true" (no content types available)`);
          }
        }
        
        // Add more detailed logging about the flagged value and content types
        console.log(`Record ${recordId}: Final flagged value = "${flaggedValue}"`);
        if (containsSensitiveInfo) {
          console.log(`Record ${recordId}: Detection summary - Found ${sensitiveContentTypes.length} type(s) of sensitive information`);
        }
        
        // Consistency check - make sure flagged status matches the containsSensitiveInfo flag
        const isFlagged = flaggedValue.startsWith('true');
        if (isFlagged !== containsSensitiveInfo) {
          console.warn(`Record ${recordId}: ⚠️ INCONSISTENCY DETECTED - containsSensitiveInfo=${containsSensitiveInfo} but flaggedValue=${flaggedValue}`);
          
          // Correct the inconsistency
          if (containsSensitiveInfo) {
            // Should be flagged but isn't
            flaggedValue = sensitiveContentTypes.length > 0 ? 
              `true (sensitive_content_types: ${sensitiveContentTypes.join(', ')})` : 
              "true";
            console.log(`Record ${recordId}: Corrected flagged value to "${flaggedValue}"`);
          } else {
            // Is flagged but shouldn't be
            flaggedValue = "false";
            console.log(`Record ${recordId}: Corrected flagged value to "false"`);
          }
        }
        
        console.log(`Record ${recordId}: OCR Text = ${ocrText.substring(0, 50)}${ocrText.length > 50 ? '...' : ''}`);
        
        // Double-check if we accidentally have a JSON string instead of parsed text
        if (ocrText.startsWith('{') && ocrText.endsWith('}') && ocrText.includes('"ocr_text"')) {
          try {
            // This might be a case where we have JSON in our ocrText - parse it again
            const nestedJson = JSON.parse(ocrText);
            if (nestedJson.ocr_text) {
              console.log(`Record ${recordId}: Found nested JSON in OCR text, extracting inner content`);
              ocrText = nestedJson.ocr_text;
            }
          } catch (e) {
            // Not valid JSON, keep as is
            console.log(`Record ${recordId}: OCR text starts with '{' but isn't valid JSON`);
          }
        }
        
        // Add to batch updates with the extracted OCR text (not the JSON)
        updates.push({
          id: recordId,
          fields: {
            [FLAGGED_FIELD]: flaggedValue,
            [OCR_DATA_FIELD]: ocrText // Store just the OCR text, not the entire JSON
          }
        });
        
      } catch (error) {
        console.error(`Error processing record ${record.id}:`, error);
      }
    }
    
    // Perform batch update if we have any updates
    if (updates.length > 0) {
      try {
        // Ensure we're not exceeding Airtable's limit of 10 records per update
        if (updates.length > 10) {
          console.warn(`Warning: Splitting ${updates.length} updates into smaller batches of 10 records each`);
          
          // Process in smaller batches of 10
          for (let j = 0; j < updates.length; j += 10) {
            const batchChunk = updates.slice(j, j + 10);
            try {
              await table.update(batchChunk);
              console.log(`✓ Updated ${batchChunk.length} records successfully (sub-batch ${Math.floor(j/10) + 1})`);
            } catch (subError) {
              console.error(`Error updating sub-batch ${Math.floor(j/10) + 1}:`, subError);
              
              // Try to update one by one if batch update fails
              console.log('Attempting to process records individually...');
              for (const record of batchChunk) {
                try {
                  await table.update([record]);
                  console.log(`✓ Updated record ${record.id} successfully`);
                } catch (recordError) {
                  console.error(`Failed to update record ${record.id}:`, recordError);
                }
              }
            }
          }
        } else {
          // If batch size is already 10 or less, update normally
          await table.update(updates);
          console.log(`✓ Updated ${updates.length} records successfully`);
        }
      } catch (error) {
        console.error('Error updating batch:', error);
        
        // Try to update one by one if batch update fails
        console.log('Attempting to process records individually...');
        for (const record of updates) {
          try {
            await table.update([record]);
            console.log(`✓ Updated record ${record.id} successfully`);
          } catch (recordError) {
            console.error(`Failed to update record ${record.id}:`, recordError);
          }
        }
      }
    }
  }
  
  console.log('Processing complete!');
}

// If running as a script
if (require.main === module) {
  // Get batch size and unprocessed flag from command line arguments
  const batchSize = process.argv[2] ? parseInt(process.argv[2]) : 10;
  const onlyUnprocessed = process.argv[3] === 'true' || process.argv[3] === '1';
  
  processOCRData(batchSize, onlyUnprocessed)
    .then(() => {
      console.log('Script completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('Script failed:', error);
      process.exit(1);
    });
}

module.exports = { processOCRData }; 