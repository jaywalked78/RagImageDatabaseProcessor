const Airtable = require('airtable');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

// Field names in Airtable
const FLAGGED_FIELD = 'Flagged';

// Main function to update flagged fields
async function batchUpdateFlaggedFields(batchSize = 10, flagValue = "false", skipValues = []) {
  console.log(`Starting Flagged field update (batch size: ${batchSize}, setting to: "${flagValue}")...`);
  
  if (skipValues.length > 0) {
    console.log(`Will skip records with these flagged values: ${JSON.stringify(skipValues)}`);
  }
  
  // Stats tracking
  let totalProcessed = 0;
  let totalUpdated = 0;
  let totalSkipped = 0;
  
  // Process records in batches using pagination
  let hasMorePages = true;
  let offset = null;
  let batchCounter = 0;
  
  while (hasMorePages) {
    batchCounter++;
    console.log(`Fetching batch ${batchCounter}...`);
    
    // Fetch only a single batch of records
    const fetchOptions = {
      pageSize: batchSize,
      sort: [{ field: 'FrameID', direction: 'asc' }]
    };
    
    if (offset) {
      fetchOptions.offset = offset;
    }
    
    // Fetch a batch of records
    const result = await table.select(fetchOptions).firstPage();
    
    // Get the offset for the next page (if any)
    if (result._pagination && result._pagination.offset) {
      offset = result._pagination.offset;
    } else {
      hasMorePages = false;
    }
    
    // If no records returned, we're done
    if (result.length === 0) {
      console.log(`No more records to process.`);
      hasMorePages = false;
      break;
    }
    
    console.log(`Processing batch ${batchCounter} (${result.length} records)...`);
    totalProcessed += result.length;
    
    // Prepare updates
    const updates = [];
    
    for (const record of result) {
      const currentValue = record.get(FLAGGED_FIELD);
      
      // Skip if current value is in skipValues
      if (skipValues.includes(currentValue)) {
        console.log(`Skipping record ${record.id}: current value = "${currentValue}"`);
        totalSkipped++;
        continue;
      }
      
      // Add to updates if not skipped
      updates.push({
        id: record.id,
        fields: {
          [FLAGGED_FIELD]: flagValue
        }
      });
    }
    
    // Skip this batch if no updates needed
    if (updates.length === 0) {
      console.log(`Batch ${batchCounter}: No records to update after filtering.`);
      continue;
    }
    
    // Perform the update
    try {
      await table.update(updates);
      console.log(`✓ Updated batch ${batchCounter} successfully (${updates.length} records)`);
      totalUpdated += updates.length;
    } catch (error) {
      console.error(`Error updating batch ${batchCounter}:`, error);
      
      // Try to update one by one if batch update fails
      console.log('Attempting to process records individually...');
      for (const record of updates) {
        try {
          await table.update([record]);
          console.log(`✓ Updated record ${record.id} successfully`);
          totalUpdated++;
        } catch (recordError) {
          console.error(`Failed to update record ${record.id}:`, recordError);
        }
      }
    }
    
    // Add a delay between batches to avoid rate limiting
    if (hasMorePages) {
      console.log('Waiting 500ms before next batch...');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  console.log(`Update complete!`);
  console.log(`Total records processed: ${totalProcessed}`);
  console.log(`Total records updated: ${totalUpdated}`);
  console.log(`Total records skipped: ${totalSkipped}`);
  
  return { 
    processed: totalProcessed, 
    updated: totalUpdated, 
    skipped: totalSkipped 
  };
}

// Command line arguments
const batchSize = process.argv[2] ? parseInt(process.argv[2]) : 10;
const flagValue = process.argv[3] || "false";
const skipValues = process.argv.slice(4); // Any additional arguments are values to skip

// Run the update
batchUpdateFlaggedFields(batchSize, flagValue, skipValues)
  .then(result => {
    console.log(`Successfully processed ${result.processed} records, updated ${result.updated} records with Flagged="${flagValue}"`);
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 