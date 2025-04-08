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

// Main test function
async function testAirtableUpdate() {
  console.log('Starting Airtable update test...');
  console.log(`Using BASE_ID: ${BASE_ID}`);
  console.log(`Using TABLE_NAME: ${TABLE_NAME}`);
  
  try {
    // Fetch a small number of records
    console.log('Fetching 3 records...');
    const records = await table.select({
      maxRecords: 3,
      sort: [{ field: 'FrameID', direction: 'asc' }]
    }).all();
    
    if (records.length === 0) {
      console.log('No records found! Aborting test.');
      return;
    }
    
    console.log(`Found ${records.length} records to test with.`);
    
    // Display the current values
    for (const record of records) {
      console.log(`Record ${record.id}: Current Flagged value = "${record.get(FLAGGED_FIELD) || 'empty'}"`);
    }
    
    // Prepare updates with a test value
    const timestamp = new Date().toISOString();
    const testValue = `TEST UPDATE ${timestamp}`;
    
    const updates = records.map(record => ({
      id: record.id,
      fields: {
        [FLAGGED_FIELD]: testValue
      }
    }));
    
    // Perform the update
    console.log(`Updating ${updates.length} records with test value: "${testValue}"`);
    await table.update(updates);
    console.log('Update completed. Fetching records again to verify...');
    
    // Fetch the same records again to verify the update
    const updatedRecords = await table.select({
      maxRecords: 3,
      filterByFormula: `OR(${records.map(r => `RECORD_ID() = '${r.id}'`).join(',')})`,
    }).all();
    
    // Display the updated values
    for (const record of updatedRecords) {
      const flaggedValue = record.get(FLAGGED_FIELD) || 'empty';
      console.log(`Record ${record.id}: Updated Flagged value = "${flaggedValue}"`);
      
      // Check if the update was successful
      if (flaggedValue === testValue) {
        console.log(`✓ Update verified for record ${record.id}`);
      } else {
        console.log(`✗ Update FAILED for record ${record.id}! Expected "${testValue}" but got "${flaggedValue}"`);
      }
    }
    
    console.log('Test completed.');
  } catch (error) {
    console.error('Error during test:', error);
  }
}

// Run the test
testAirtableUpdate().then(() => {
  console.log('Script finished.');
  process.exit(0);
}).catch(error => {
  console.error('Script failed:', error);
  process.exit(1);
}); 