const Airtable = require('airtable');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

async function checkFieldNames() {
  console.log('Checking Airtable field names and sample data...');
  console.log(`Base ID: ${BASE_ID}`);
  console.log(`Table Name: ${TABLE_NAME}`);
  
  try {
    // Fetch a few records
    const records = await table.select({ maxRecords: 3 }).firstPage();
    
    if (records.length === 0) {
      console.log('No records found in table.');
      return;
    }
    
    // Get the first record to examine field names
    const firstRecord = records[0];
    console.log(`\nRecord ID: ${firstRecord.id}`);
    console.log('Field names in this record:');
    
    // Get and display all field names
    const fields = firstRecord.fields;
    for (const [fieldName, fieldValue] of Object.entries(fields)) {
      console.log(`- ${fieldName}: ${typeof fieldValue === 'object' ? JSON.stringify(fieldValue).substring(0, 50) + '...' : fieldValue}`);
    }
    
    // Check for specific fields we're interested in
    console.log('\nChecking for specific fields:');
    const interestingFields = [
      'FolderPath', 
      'FramePath', 
      'FilePath',
      'Path',
      'ImagePath',
      'FullPath',
      'OCRData',
      'Flagged',
      'SensitivityConcerns'
    ];
    
    for (const field of interestingFields) {
      const exists = fields.hasOwnProperty(field);
      console.log(`- ${field}: ${exists ? 'EXISTS' : 'NOT FOUND'}`);
      if (exists) {
        console.log(`  Value: ${fields[field]}`);
      }
    }
    
    // Display all data for all records
    console.log('\nAll fields for first 3 records:');
    records.forEach((record, index) => {
      console.log(`\nRecord ${index + 1} (ID: ${record.id}):`);
      for (const [fieldName, fieldValue] of Object.entries(record.fields)) {
        console.log(`- ${fieldName}: ${typeof fieldValue === 'object' ? JSON.stringify(fieldValue).substring(0, 50) + '...' : fieldValue}`);
      }
    });
    
  } catch (error) {
    console.error('Error checking field names:', error);
  }
}

// Run the function
checkFieldNames()
  .then(() => {
    console.log('Check completed');
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 