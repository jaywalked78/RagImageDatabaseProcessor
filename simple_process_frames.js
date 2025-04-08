const Airtable = require('airtable');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

// Field names
const OCR_DATA_FIELD = 'OCRData';
const FLAGGED_FIELD = 'Flagged';

// Process each batch of records
async function processFrames(batchSize = 10) {
  console.log(`Starting to process frames with batch size: ${batchSize}`);
  
  // Process records in batches using pagination
  let hasMorePages = true;
  let offset = null;
  let batchCounter = 0;
  
  while (hasMorePages) {
    batchCounter++;
    console.log(`\nFetching batch ${batchCounter}...`);
    
    // Configure fetch options with pagination
    const fetchOptions = {
      pageSize: batchSize,
      sort: [{ field: 'FrameID', direction: 'asc' }]
    };
    
    if (offset) {
      fetchOptions.offset = offset;
    }
    
    // Fetch the current batch
    const batch = await table.select(fetchOptions).firstPage();
    
    // If nothing returned, we're done
    if (batch.length === 0) {
      console.log('No more records to process.');
      hasMorePages = false;
      break;
    }
    
    // Get pagination information for next batch
    if (batch._pagination && batch._pagination.offset) {
      offset = batch._pagination.offset;
    } else {
      hasMorePages = false;
    }
    
    console.log(`Processing batch ${batchCounter} (${batch.length} records)...`);
    
    // Process each record in the batch
    const updates = [];
    
    for (const record of batch) {
      try {
        const recordId = record.id;
        const ocrDataString = record.get(OCR_DATA_FIELD);
        
        // Default values
        let flaggedValue = "false";
        let containsSensitiveInfo = false;
        let sensitiveContentTypes = [];
        
        // If OCR data exists, analyze it
        if (ocrDataString) {
          // Check if it's in JSON format
          if (ocrDataString.startsWith('{') && ocrDataString.includes('"ocr_text"')) {
            try {
              const legacyData = JSON.parse(ocrDataString);
              containsSensitiveInfo = !!legacyData.contains_sensitive_info;
              
              if (legacyData.sensitive_content_types) {
                if (Array.isArray(legacyData.sensitive_content_types)) {
                  sensitiveContentTypes = legacyData.sensitive_content_types;
                } else if (typeof legacyData.sensitive_content_types === 'string') {
                  sensitiveContentTypes = legacyData.sensitive_content_types.split(',').map(type => type.trim());
                }
              }
            } catch (jsonError) {
              console.error(`Error parsing legacy JSON for record ${recordId}:`, jsonError);
              
              // Try to extract info using regex
              const sensitiveMatch = ocrDataString.match(/"contains_sensitive_info"\s*:\s*(true|false)/);
              containsSensitiveInfo = sensitiveMatch ? (sensitiveMatch[1] === "true") : false;
            }
          } else {
            // Simple text check for sensitive patterns
            containsSensitiveInfo = /password|api.?key|token|secret|credit.?card|ssn|social.?security/i.test(ocrDataString);
            
            if (containsSensitiveInfo) {
              sensitiveContentTypes = ['auto_detected'];
            }
          }
        }
        
        // Set flagged value based on sensitive content
        if (containsSensitiveInfo) {
          if (sensitiveContentTypes.length > 0) {
            // Clean up the types
            const uniqueTypes = [...new Set(sensitiveContentTypes.map(t => t.toString().replace(/["'\[\]{}]/g, '').trim()))];
            flaggedValue = `true (sensitive_content_types: ${uniqueTypes.join(', ')})`;
          } else {
            flaggedValue = "true";
          }
        }
        
        // Add to batch updates
        updates.push({
          id: recordId,
          fields: {
            [FLAGGED_FIELD]: flaggedValue
          }
        });
        
      } catch (error) {
        console.error(`Error processing record ${record.id}:`, error);
      }
    }
    
    // Update records in Airtable
    if (updates.length > 0) {
      try {
        await table.update(updates);
        console.log(`✓ Updated ${updates.length} records successfully`);
      } catch (error) {
        console.error('Error updating batch:', error);
        
        // Try to update records one by one if batch update fails
        console.log('Attempting to update records individually...');
        let successCount = 0;
        
        for (const record of updates) {
          try {
            await table.update([record]);
            successCount++;
          } catch (individualError) {
            console.error(`Failed to update record ${record.id}:`, individualError);
          }
        }
        
        console.log(`✓ Successfully updated ${successCount}/${updates.length} records individually`);
      }
    }
    
    // Add a short delay to avoid rate limiting
    if (hasMorePages) {
      console.log('Waiting 500ms before next batch...');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  console.log('\nProcessing complete!');
}

// Parse command line arguments
const batchSize = process.argv[2] ? parseInt(process.argv[2]) : 10;

// Run the processor
processFrames(batchSize)
  .then(() => {
    console.log('Script completed successfully');
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 