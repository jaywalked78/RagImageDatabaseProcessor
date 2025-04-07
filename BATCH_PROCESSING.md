# Batch Processing with Airtable and Google Drive

This document explains how to use the batch processing feature to automatically process frames from Airtable and Google Drive.

## Prerequisites

Before you begin, you need:

1. An Airtable base with frame metadata
2. Google Drive containing the actual frame images
3. A Google Drive service account
4. Required environment variables configured

## Setting Up the Environment

### 1. Install Required Packages

The batch processing feature requires additional Python packages. These are included in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2. Configure Google Drive Service Account

Run the setup script for guidance:

```bash
./setup_google_drive.sh
```

Follow the instructions to:
- Create a Google Cloud project
- Enable Google Drive API
- Create a service account
- Download the service account key
- Share your Google Drive folders with the service account

### 3. Configure Airtable API Key

1. Get your Airtable API key from https://airtable.com/account
2. Add it to your `.env` file:

```
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_NAME=Frames
```

### 4. Configure Field Mappings

Ensure your Airtable table has the necessary fields and update the `.env` file with the correct field names:

```
DRIVE_FILE_ID_FIELD=DriveFileID  # Field containing Google Drive file IDs
FRAME_NUMBER_FIELD=FrameNumber
VIDEO_ID_FIELD=VideoID
TIMESTAMP_FIELD=Timestamp
TITLE_FIELD=Title
PROCESSED_FIELD=Processed  # Boolean field to track processing status
```

## Airtable Structure Requirements

Your Airtable table should have at least these columns:

| Field        | Type     | Description                                   |
|--------------|----------|-----------------------------------------------|
| DriveFileID  | Text     | The Google Drive file ID for the frame image  |
| VideoID      | Text     | Identifier for the source video               |
| FrameNumber  | Number   | Frame number within the video                 |
| Timestamp    | Number   | Timestamp of the frame in seconds (optional)  |
| Title        | Text     | Description of the frame (optional)           |
| Processed    | Checkbox | Whether the frame has been processed          |

## Using the API

### Start a Batch Processing Job

```bash
curl -X POST "http://localhost:8777/batch/process" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_size": 20,
    "max_frames": 100,
    "update_airtable": true,
    "processed_field": "Processed",
    "download_to_disk": false
  }'
```

Parameters:
- `batch_size`: Number of frames to process in each batch (default: 20)
- `max_frames`: Maximum number of frames to process (default: all unprocessed frames)
- `update_airtable`: Whether to update the processed status in Airtable (default: true)
- `processed_field`: Field name in Airtable that tracks processing status (default: "Processed")
- `download_to_disk`: Whether to download files to disk or memory (default: false)

### Check Job Status

```bash
curl "http://localhost:8777/batch/status/{job_id}"
```

Replace `{job_id}` with the ID returned when starting the job.

### List All Jobs

```bash
curl "http://localhost:8777/batch/list"
```

## Using from n8n

To trigger batch processing from n8n:

1. Add an HTTP Request node
2. Set the method to POST
3. Set the URL to `http://localhost:8777/batch/process`
4. Set the "Body Content Type" to "JSON"
5. Set the JSON body:

```json
{
  "batch_size": 20,
  "max_frames": 100,
  "update_airtable": true
}
```

6. Connect this to a trigger node (like a button, schedule, or webhook)

## Monitoring and Logging

The application logs all batch processing activities. You can check:

- `logicLoom.log` for detailed logs
- `logicLoom_errors.log` for error-only logs

Increase verbosity by starting the app with `--log-level DEBUG`:

```bash
./run.sh --log-level DEBUG
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure your service account has the correct permissions and the key file is in the right location.

2. **Rate Limiting**: If processing a large number of frames, adjust the `batch_size` parameter to avoid hitting API rate limits.

3. **Memory Issues**: For large images, set `download_to_disk` to `true` to avoid loading everything into memory.

4. **File Not Found**: Ensure the Google Drive file IDs in Airtable are correct and the service account has access to those files.

5. **Database Errors**: Check that your PostgreSQL connection details are correct and the database is running. 