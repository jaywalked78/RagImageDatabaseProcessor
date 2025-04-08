// Test script for parse_ocr_data.js
const fs = require('fs');
const parse_ocr_data = require('./parse_ocr_data');

// Directly patch the Airtable module
const Airtable = require('airtable');
const BASE_ID = process.env.AIRTABLE_BASE_ID || 'test_base_id';
const TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis';
const API_KEY = process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN || 'test_api_key';

// Create a test record with our sample data
const testRecord = {
  id: 'test_record_1',
  _rawJson: {
    fields: {
      OCRData: fs.readFileSync('test_data.txt', 'utf8'),
      Flagged: ''
    }
  },
  get: function(fieldName) {
    return this._rawJson.fields[fieldName];
  }
};

// Monkey patch the Airtable base function
Airtable.Base = function() {
  this.table = function() {
    return {
      select: function() {
        return {
          all: function() {
            console.log('Returning mock record with test data');
            return Promise.resolve([testRecord]);
          }
        };
      },
      update: function(records) {
        console.log('MOCK UPDATE RESULT:');
        console.log(JSON.stringify(records, null, 2));
        return Promise.resolve(records);
      }
    };
  };
  return this;
};

// Monkey patch the Airtable constructor
Airtable.prototype.base = function(baseId) {
  console.log(`Mock Airtable.base called with baseId: ${baseId}`);
  return function(tableName) {
    console.log(`Mock table function called with tableName: ${tableName}`);
    return {
      select: function() {
        console.log('Mock select function called');
        return {
          all: function() {
            console.log('Mock all function called - returning test data');
            return Promise.resolve([testRecord]);
          }
        };
      },
      update: function(records) {
        console.log('MOCK UPDATE RESULT:');
        console.log(JSON.stringify(records, null, 2));
        return Promise.resolve(records);
      }
    };
  };
};

console.log('Running test with sample sensitive data:');
console.log(fs.readFileSync('test_data.txt', 'utf8'));
console.log('----------------------------------');

// Run the processor
parse_ocr_data.processOCRData(1, false).then(() => {
  console.log('Test completed');
}); 