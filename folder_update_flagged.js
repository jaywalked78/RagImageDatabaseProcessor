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
const FOLDER_NAME_FIELD = 'FolderName';

// Main function to update flagged fields by folder
async function updateFlaggedByFolder(flagValue = "false", skipValues = [], specificFolder = null) {
  console.log(`Starting Flagged field update by folder (setting to: "${flagValue}")...`);
  
  if (skipValues.length > 0) {
    console.log(`Will skip records with these flagged values: ${JSON.stringify(skipValues)}`);
  }
  
  // Stats tracking
  let totalFolders = 0;
  let totalProcessed = 0;
  let totalUpdated = 0;
  let totalSkipped = 0;
  
  try {
    // Step 1: Get all unique folder names if no specific folder is provided
    let folders = [];
    
    if (specificFolder) {
      folders = [specificFolder];
      console.log(`Processing specific folder: ${specificFolder}`);
    } else {
      console.log('Getting list of unique folders...');
      
      // Get all records but only fetch the FolderName field to save bandwidth
      const allRecords = await table.select({
        fields: [FOLDER_NAME_FIELD]
      }).all();
      
      // Extract unique folder names
      const folderSet = new Set();
      allRecords.forEach(record => {
        const folderName = record.get(FOLDER_NAME_FIELD);
        if (folderName) {
          folderSet.add(folderName);
        }
      });
      
      folders = Array.from(folderSet);
      console.log(`Found ${folders.length} unique folders.`);
    }
    
    // Step 2: Process each folder
    for (const folderName of folders) {
      totalFolders++;
      console.log(`\nProcessing folder ${totalFolders}/${folders.length}: "${folderName}"`);
      
      // Get all records for this folder
      const folderRecords = await table.select({
        filterByFormula: `{${FOLDER_NAME_FIELD}} = "${folderName.replace(/"/g, '\\"')}"`,
        sort: [{ field: 'FrameID', direction: 'asc' }]
      }).all();
      
      console.log(`Found ${folderRecords.length} records in folder "${folderName}"`);
      totalProcessed += folderRecords.length;
      
      // Skip empty folders
      if (folderRecords.length === 0) {
        console.log(`Skipping empty folder: "${folderName}"`);
        continue;
      }
      
      // Prepare updates
      const updates = [];
      
      for (const record of folderRecords) {
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
      
      // Skip if no updates needed
      if (updates.length === 0) {
        console.log(`Folder "${folderName}": No records to update after filtering.`);
        continue;
      }
      
      // Process in batches of 10 (Airtable limit)
      const batchSize = 10;
      for (let i = 0; i < updates.length; i += batchSize) {
        const batch = updates.slice(i, i + batchSize);
        console.log(`Updating batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(updates.length/batchSize)} (${batch.length} records)...`);
        
        try {
          await table.update(batch);
          console.log(`✓ Updated batch successfully`);
          totalUpdated += batch.length;
        } catch (error) {
          console.error(`Error updating batch:`, error);
          
          // Try to update one by one if batch update fails
          console.log('Attempting to process records individually...');
          for (const record of batch) {
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
        if (i + batchSize < updates.length) {
          console.log('Waiting 300ms before next batch...');
          await new Promise(resolve => setTimeout(resolve, 300));
        }
      }
      
      console.log(`✓ Completed folder "${folderName}". Updated ${updates.length} records.`);
      
      // Add a delay between folders to avoid rate limiting
      if (folders.indexOf(folderName) < folders.length - 1) {
        console.log('Waiting 1 second before next folder...');
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log(`\nUpdate complete!`);
    console.log(`Total folders processed: ${totalFolders}`);
    console.log(`Total records processed: ${totalProcessed}`);
    console.log(`Total records updated: ${totalUpdated}`);
    console.log(`Total records skipped: ${totalSkipped}`);
    
    return { 
      folders: totalFolders,
      processed: totalProcessed, 
      updated: totalUpdated, 
      skipped: totalSkipped 
    };
    
  } catch (error) {
    console.error('Error in folder processing:', error);
    throw error;
  }
}

// Command line arguments
const flagValue = process.argv[2] || "false";
const specificFolder = process.argv[3] || null; // Optional specific folder to process
const skipValues = process.argv.slice(4); // Any additional arguments are values to skip

// Run the update
updateFlaggedByFolder(flagValue, skipValues, specificFolder)
  .then(result => {
    console.log(`Successfully processed ${result.folders} folders, ${result.processed} records, updated ${result.updated} records with Flagged="${flagValue}"`);
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 