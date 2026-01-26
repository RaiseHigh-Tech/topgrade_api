# Video Duration Calculation Fix

## Problem
Video duration was not being calculated in production when videos were uploaded directly to S3. The calculation only worked for traditional file uploads, not for S3 direct uploads.

## Root Cause
When videos are uploaded directly to S3 (which is the method used in production), the video file never passes through the Django server. The previous code had comments indicating duration calculation was skipped for S3 uploads:
```python
# Note: Duration calculation for S3 videos would require downloading
# which is not efficient. Consider calculating on client side or skipping.
```

## Solution
Implemented a complete solution that calculates video duration for S3-uploaded videos by:

1. **New Function**: `calculate_video_duration_from_s3(s3_key)`
   - Downloads video temporarily from S3
   - Calculates duration using moviepy or OpenCV
   - Cleans up temporary files
   - Returns formatted duration string (MM:SS or HH:MM:SS)

2. **Updated Program Views**: Modified three locations in `dashboard/views/program_view.py`:
   - Creating new programs with S3 videos
   - Updating existing topics with S3 videos
   - Adding new topics with S3 videos

3. **Celery Background Tasks**: Added async processing for large videos
   - `calculate_video_duration_task`: Process single video in background
   - `calculate_video_durations_bulk`: Process multiple videos at once

4. **Management Command**: Created utility to fix existing videos
   - `calculate_missing_video_durations`: Finds and processes videos without duration

## Files Modified

### 1. `dashboard/views/program_view.py`
- Added `calculate_video_duration_from_s3()` function
- Updated three S3 video handling sections to call duration calculation
- Added proper error handling and user warnings

### 2. `dashboard/tasks.py`
- Added `calculate_video_duration_task()` - Background processing for single video
- Added `calculate_video_durations_bulk()` - Batch processing for multiple videos

### 3. New Management Command
- Created `dashboard/management/commands/calculate_missing_video_durations.py`
- Supports various options for flexible processing

## Usage

### For New Videos
Duration is now automatically calculated when videos are uploaded via S3. No additional steps needed.

### For Existing Videos Without Duration

#### Option 1: Check what needs fixing (Dry Run)
```bash
python manage.py calculate_missing_video_durations --dry-run
```

#### Option 2: Fix all videos synchronously
```bash
python manage.py calculate_missing_video_durations
```

#### Option 3: Fix all videos asynchronously (Recommended for Production)
```bash
python manage.py calculate_missing_video_durations --async
```

#### Option 4: Fix specific topic
```bash
python manage.py calculate_missing_video_durations --topic-id 123
```

#### Option 5: Fix all topics in a program
```bash
python manage.py calculate_missing_video_durations --program-id 5
```

### Using Celery Tasks Directly

```python
from dashboard.tasks import calculate_video_duration_task, calculate_video_durations_bulk

# Calculate duration for a single topic
task = calculate_video_duration_task.delay(topic_id=123)

# Calculate durations for multiple topics
topic_ids = [1, 2, 3, 4, 5]
result = calculate_video_durations_bulk.delay(topic_ids)
```

## Technical Details

### Video Duration Calculation Process

1. **S3 Download**: Video is downloaded from S3 to a temporary file
2. **Duration Extraction**: 
   - First tries moviepy (more reliable)
   - Falls back to OpenCV if moviepy fails
3. **Cleanup**: Temporary file is always deleted
4. **Format**: Returns duration as "MM:SS" or "HH:MM:SS"

### Error Handling

- Graceful fallback between moviepy and OpenCV
- Proper error logging for debugging
- User-friendly warning messages in the UI
- Videos are saved even if duration calculation fails

### S3 Key Handling

The function handles both S3 key formats:
- With `media/` prefix: `media/programs/advanced/program_name/video.mp4`
- Without prefix: `programs/advanced/program_name/video.mp4`

It tries both formats to ensure compatibility.

## Dependencies

Required Python packages (already in `requirements.txt`):
- `opencv-python` - Video processing
- `moviepy` - Video processing (primary method)
- `boto3` - AWS S3 client

## Configuration

Ensure these settings are configured in production:
```python
USE_S3 = True
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'your-region'
```

## Testing

Run the test script to verify setup:
```bash
python manage.py shell < tmp_rovodev_test_duration_calculation.py
```

This will check:
- Required libraries are installed
- S3 configuration is correct
- Topics missing duration
- Duration formatting function

## Performance Considerations

### Synchronous Processing
- Good for: Small videos, low traffic periods
- Impact: Blocks request until calculation completes
- Use when: Processing < 10 videos

### Asynchronous Processing (Recommended)
- Good for: Large videos, production environments
- Impact: No blocking, processes in background
- Use when: Processing many videos or in production

### Background Task Processing
Each video download and processing takes approximately:
- Small videos (< 10MB): 5-15 seconds
- Medium videos (10-50MB): 15-30 seconds
- Large videos (50MB+): 30-60+ seconds

Times depend on:
- S3 download speed
- Video codec complexity
- Server resources

## Monitoring

Check Celery logs for background task progress:
```bash
celery -A topgrade worker --loglevel=info
```

Check Django logs for synchronous processing:
```bash
tail -f /path/to/django/logs
```

## Troubleshooting

### Issue: Duration not calculated
**Check:**
1. S3 credentials are correct
2. Video file exists in S3
3. moviepy and opencv-python are installed
4. Check logs for specific error messages

### Issue: Timeout during calculation
**Solution:**
Use async processing instead:
```bash
python manage.py calculate_missing_video_durations --async
```

### Issue: Wrong duration format
**Verify:**
- Check the `format_duration()` function output
- Ensure video file is not corrupted

## Future Enhancements

Potential improvements:
1. Calculate duration on client-side before upload
2. Cache calculated durations
3. Add progress indicator in UI
4. Parallel processing for bulk operations
5. Store video metadata (resolution, codec, etc.)

## Support

For issues or questions:
- Check logs first: `/var/log/django/` or console output
- Verify S3 configuration
- Test with a single video first
- Use dry-run mode to identify problems

---

**Last Updated**: 2026-01-26
**Author**: RovoDev
**Status**: ✅ Production Ready
