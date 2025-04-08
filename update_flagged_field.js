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
async function updateFlaggedFields(batchSize = 10, flagValue = "false", skipExisting = false, skipValues = []) {
  console.log(`Starting Flagged field update (batch size: ${batchSize}, setting to: "${flagValue}")...`);
  if (skipExisting) {
    console.log(`Will skip records that already have a flagged value.`);
  }
  if (skipValues.length > 0) {
    console.log(`Will skip records with these flagged values: ${JSON.stringify(skipValues)}`);
  }
  
  // Fetch all records
  console.log('Fetching records...');
  const records = await table.select({
    sort: [{ field: 'FrameID', direction: 'asc' }]
  }).all();
  
  console.log(`Found ${records.length} records total.`);
  
  // Process records in batches
  let totalUpdated = 0;
  let totalSkipped = 0;
  
  for (let i = 0; i < records.length; i += batchSize) {
    const batch = records.slice(i, i + batchSize);
    console.log(`Processing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(records.length/batchSize)} (${batch.length} records)...`);
    
    // Prepare batch updates, skipping records if needed
    const updates = [];
    for (const record of batch) {
      const currentValue = record.get(FLAGGED_FIELD);
      
      // Skip logic
      let shouldSkip = false;
      
      // Skip if record already has a flag and skipExisting is true
      if (skipExisting && currentValue) {
        shouldSkip = true;
      }
      
      // Skip if current value is in skipValues
      if (skipValues.includes(currentValue)) {
        shouldSkip = true;
      }
      
      if (shouldSkip) {
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
      console.log(`Batch ${Math.floor(i/batchSize) + 1}: No records to update after filtering.`);
      continue;
    }
    
    // Perform batch update
    try {
      await table.update(updates);
      console.log(`✓ Updated batch ${Math.floor(i/batchSize) + 1} successfully (${updates.length} records)`);
      totalUpdated += updates.length;
    } catch (error) {
      console.error(`Error updating batch ${Math.floor(i/batchSize) + 1}:`, error);
      
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
    
    // Add a small delay between batches to avoid rate limiting
    if (i + batchSize < records.length) {
      console.log('Waiting 500ms before next batch...');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  console.log(`Update complete! Updated ${totalUpdated} records, skipped ${totalSkipped} records.`);
  return { updated: totalUpdated, skipped: totalSkipped };
}

// Command line arguments
const batchSize = process.argv[2] ? parseInt(process.argv[2]) : 10;
const flagValue = process.argv[3] || "false";
const skipExisting = process.argv[4] === "true";
const skipValues = process.argv.slice(5); // Any additional arguments are values to skip

// Run the update
updateFlaggedFields(batchSize, flagValue, skipExisting, skipValues)
  .then(result => {
    console.log(`Successfully updated ${result.updated} records to Flagged="${flagValue}"`);
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 