# API Quick Start Guide

## Starting the API Server

```bash
cd backend
python api_endpoints.py
```

The server will start on `http://localhost:5000`

## Testing the API

### 1. Check System Status
```bash
curl http://localhost:5000/api/system/status
```

### 2. Upload a Photo
```bash
curl -X POST http://localhost:5000/api/photos/upload \
  -F "file=@/path/to/photo.jpg" \
  -F "event_id=my_event"
```

### 3. Process Event Directory
```bash
curl -X POST http://localhost:5000/api/photos/process-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "my_event",
    "photos_dir": "/path/to/photos",
    "force_reprocess": false
  }'
```

### 4. Capture Face from Webcam
```bash
curl -X POST http://localhost:5000/api/scan/capture \
  -H "Content-Type: application/json" \
  -d '{
    "camera_index": 0,
    "timeout": 30,
    "min_quality": 0.5
  }'
```

### 5. Scan and Match
```bash
curl -X POST http://localhost:5000/api/scan/match \
  -H "Content-Type: application/json" \
  -d '{
    "camera_index": 0,
    "timeout": 30
  }'
```

### 6. Get Person Photos
```bash
curl "http://localhost:5000/api/search/person/1/photos?type=all&limit=10"
```

### 7. Find Similar Faces
```bash
curl -X POST http://localhost:5000/api/search/similar-faces \
  -F "file=@/path/to/face.jpg" \
  -F "top_k=5"
```

### 8. Reset Cache
```bash
curl -X POST http://localhost:5000/api/system/reset-cache
```

## Running Tests

```bash
cd backend
python test_api_endpoints.py
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed",
  "data": {
    /* response data */
  },
  "timestamp": "2023-11-23T18:30:00"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2023-11-23T18:30:00"
}
```

## Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (endpoint doesn't exist)
- `405`: Method Not Allowed (wrong HTTP method)
- `413`: Payload Too Large (file > 16MB)
- `500`: Internal Server Error

## Configuration

### File Upload Limits
- Maximum file size: 16MB
- Allowed extensions: png, jpg, jpeg, gif, bmp

### Upload Directory
- Default: `../uploads`
- Event photos: `../uploads/event_{event_id}/`

## Integration with Frontend

### JavaScript Example
```javascript
// Upload photo
async function uploadPhoto(file, eventId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('event_id', eventId);
  
  const response = await fetch('http://localhost:5000/api/photos/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Get person photos
async function getPersonPhotos(personId, type = 'all', limit = 50) {
  const response = await fetch(
    `http://localhost:5000/api/search/person/${personId}/photos?type=${type}&limit=${limit}`
  );
  
  return await response.json();
}
```

### Python Example
```python
import requests

# Upload photo
def upload_photo(file_path, event_id):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'event_id': event_id}
        response = requests.post(
            'http://localhost:5000/api/photos/upload',
            files=files,
            data=data
        )
    return response.json()

# Get person photos
def get_person_photos(person_id, photo_type='all', limit=50):
    response = requests.get(
        f'http://localhost:5000/api/search/person/{person_id}/photos',
        params={'type': photo_type, 'limit': limit}
    )
    return response.json()
```

## Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check database connection

### Upload fails
- Verify file size < 16MB
- Check file extension is allowed
- Ensure upload directory exists and is writable

### Webcam capture fails
- Verify webcam is connected
- Check camera permissions
- Try different camera_index (0, 1, 2...)

### No faces detected
- Ensure image has visible faces
- Check image quality (not too blurry)
- Verify face size is > 30 pixels

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_endpoints:app
```

### Using uWSGI
```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file api_endpoints.py --callable app
```

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_PATH=/path/to/database.db
export UPLOAD_FOLDER=/path/to/uploads
```

## Security Considerations

- Use HTTPS in production
- Implement authentication for sensitive endpoints
- Add rate limiting
- Validate all user inputs
- Sanitize file uploads
- Use environment variables for secrets

## Performance Tips

- Enable caching for frequently accessed data
- Use connection pooling for database
- Implement async processing for batch operations
- Add CDN for static files
- Monitor and optimize slow endpoints

## Support

For issues or questions:
1. Check the logs in the console
2. Review error messages in API responses
3. Verify all components are initialized
4. Test with the provided test suite
