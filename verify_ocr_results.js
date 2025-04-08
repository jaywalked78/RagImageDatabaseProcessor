const Airtable = require('airtable');
require('dotenv').config();

// Configure Airtable
const BASE_ID = process.env.AIRTABLE_BASE_ID;
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN;

const base = new Airtable({ apiKey: API_KEY }).base(BASE_ID);
const table = base(TABLE_NAME);

async function verifyOCRResults() {
  console.log('Verifying OCR results in Airtable...');
  console.log(`Base ID: ${BASE_ID}`);
  console.log(`Table Name: ${TABLE_NAME}`);
  
  try {
    // Fetch recently processed records
    console.log('Fetching records with OCRData field...');
    const records = await table.select({
      filterByFormula: "NOT({OCRData} = '')",
      sort: [{ field: 'FrameNumber', direction: 'asc' }],
      maxRecords: 10
    }).firstPage();
    
    if (records.length === 0) {
      console.log('No records found with OCRData.');
      return;
    }
    
    console.log(`Found ${records.length} records with OCR data.`);
    
    // Display results for each record
    records.forEach((record, index) => {
      const fields = record.fields;
      console.log(`\nRecord ${index + 1} (ID: ${record.id}):`);
      console.log(`- FrameNumber: ${fields.FrameNumber || 'N/A'}`);
      console.log(`- FolderPath: ${fields.FolderPath || 'N/A'}`);
      console.log(`- Flagged: ${fields.Flagged || 'N/A'}`);
      
      if (fields.SensitivityConcerns) {
        console.log(`- SensitivityConcerns: ${fields.SensitivityConcerns}`);
      } else {
        console.log(`- SensitivityConcerns: None`);
      }
      
      // Show a sample of the OCR text
      if (fields.OCRData) {
        const ocrSample = fields.OCRData.substr(0, 150);
        console.log(`- OCRData (sample): ${ocrSample}${fields.OCRData.length > 150 ? '...' : ''}`);
      } else {
        console.log(`- OCRData: None`);
      }
    });
    
    // Provide a summary of flagged vs unflagged records
    const flaggedRecords = records.filter(record => record.fields.Flagged === 'true');
    console.log(`\nSummary: ${flaggedRecords.length} of ${records.length} records are flagged as sensitive.`);
    
  } catch (error) {
    console.error('Error verifying OCR results:', error);
  }
}

// Run the function
verifyOCRResults()
  .then(() => {
    console.log('\nVerification completed');
    process.exit(0);
  })
  .catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
  }); 