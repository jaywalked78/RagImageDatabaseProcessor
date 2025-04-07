# Airtable Schema Configuration

This document outlines the recommended Airtable schema configuration for the frame processing system's OCR data integration.

## Table Setup

Create a table named `FrameData` (or your preferred name) with the following fields:

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Name | Single line text | Name of the frame (auto-filled by Airtable) |
| FrameID | Single line text | Unique identifier for the frame (required for matching) |
| FilePath | Single line text | Original path to the frame file |
| Timestamp | Date & Time | When the frame was captured or processed |
| OCRData | Long text | Structured text data extracted via OCR |
| OCRWordCount | Number | Number of words in extracted text |
| OCRCharCount | Number | Number of characters in extracted text |
| OCRTopics | Multiple select | Main topics detected in the text |
| OCRContentTypes | Multiple select | Types of content detected (tables, paragraphs, etc.) |
| OCRContainsURLs | Checkbox | Whether the frame contains URLs |
| OCRContainsTables | Checkbox | Whether the frame contains tables |
| OCRLastUpdated | Date & Time | When OCR data was last processed |
| Flagged | Checkbox | Whether the frame contains sensitive information |

## Field Configuration

### Required Fields

The following fields are required for the integration to work:

- **FrameID**: Must match the frame ID in your processed_frames.csv file (usually the filename without extension)
- **OCRData**: Stores the structured text extracted from frames
- **Flagged**: Indicates frames containing sensitive information

### Optional Fields

The other fields are optional but recommended for better data organization.

### Multiple Select Options

For the multiple select fields, you may want to configure these options:

**OCRTopics**:
- General
- Technical
- Business
- Creative
- Personal
- Financial
- Educational
- Entertainment
- Other

**OCRContentTypes**:
- paragraph
- table
- list
- heading
- code
- api_key
- credentials
- url
- contact_info
- date_time

## Example Configuration

1. Create a new base in Airtable
2. Create a table named "FrameData"
3. Configure the fields as described above
4. Get your Base ID from the API documentation (https://airtable.com/api)
5. Generate an API key in your account settings
6. Update your `.env.airtable` file with the credentials

## Testing the Connection

Run the following command to test your Airtable connection:

```bash
./scripts/update_airtable.sh --storage-dir all_frame_embeddings
```

If everything is configured correctly, your Airtable base will be populated with OCR data from your processed frames. 