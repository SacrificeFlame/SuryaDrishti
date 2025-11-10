# Debugging API Errors Guide

## Quick Debug Endpoints

### 1. Test External API Connection
```
GET http://localhost:8000/api/v1/debug/test-external-api
```

This endpoint will:
- Test the connection to the external API
- Return detailed error information
- Show request/response details
- Provide diagnosis of the issue

**Example Response (Success)**:
```json
{
  "status": "success",
  "request": {
    "url": "https://aecial-romona-unwrested.ngrok-free.dev/api/run",
    "method": "POST",
    "headers": {...},
    "body": {"source": "hybrid"}
  },
  "response": {
    "status_code": 200,
    "text": "...",
    "json": {...}
  },
  "diagnosis": {
    "connection": "ok",
    "api_responded": true,
    "status_ok": true
  }
}
```

**Example Response (Error)**:
```json
{
  "status": "error",
  "error": {
    "type": "connection_error",
    "message": "Connection refused",
    "url": "..."
  },
  "diagnosis": {
    "connection": "failed",
    "api_responded": false,
    "possible_causes": [
      "ngrok URL is down or expired",
      "Network connectivity issue",
      "API server is not running"
    ]
  }
}
```

### 2. Get API Configuration
```
GET http://localhost:8000/api/v1/debug/api-config
```

Returns current API configuration (without exposing full API key).

---

## Enable Debug Mode

To see detailed error information in the forecast endpoint responses:

### Option 1: Environment Variable
Set `DEBUG=true` in your environment:
```bash
# Windows PowerShell
$env:DEBUG="true"

# Linux/Mac
export DEBUG=true
```

### Option 2: Backend .env file
Add to `backend/.env`:
```
DEBUG=true
```

When debug mode is enabled, the `/api/v1/forecast/schedule` endpoint will return:
```json
{
  "status": "error",
  "error": {
    "status_code": 400,
    "error_text": "Detailed error message here",
    "url": "...",
    "headers": {...}
  },
  "message": "External API error - see error details above",
  "fallback": "Using mock data",
  "mock_data": {...}
}
```

---

## Common Error Scenarios

### 1. Connection Timeout
**Symptom**: Request times out after 35 seconds
**Possible Causes**:
- External API is slow or overloaded
- Network connectivity issues
- ngrok tunnel is slow

**Solution**:
- Check if external API is accessible
- Verify ngrok URL is active
- Check network connection

### 2. Status Code 400/500
**Symptom**: API returns error status code
**Possible Causes**:
- Invalid request format
- API key is incorrect
- API endpoint changed
- Request body format incorrect

**Solution**:
- Check error text in response
- Verify API key is correct
- Check if API expects different format
- Test API directly with curl

### 3. Connection Refused
**Symptom**: Cannot connect to external API
**Possible Causes**:
- ngrok URL expired
- External API server is down
- Network firewall blocking

**Solution**:
- Verify ngrok URL is active
- Check if external API is running
- Test with curl directly

---

## Testing External API Directly

### Using curl:
```bash
curl -X POST "https://aecial-romona-unwrested.ngrok-free.dev/api/run" \
  -H "Content-Type: application/json" \
  -H "x-api-key: aryan1234%^&*()" \
  -d '{"source": "hybrid"}'
```

### Using JavaScript (Browser Console):
```javascript
fetch('https://aecial-romona-unwrested.ngrok-free.dev/api/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': 'aryan1234%^&*()'
  },
  body: JSON.stringify({ source: 'hybrid' })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

---

## Frontend Error Handling

The frontend should check for errors in the response:

```typescript
const response = await fetch('/api/v1/forecast/schedule?forecast_hours=12');
const data = await response.json();

// Check for error status
if (data.status === 'error') {
  console.error('API Error:', data.error);
  // Show error to user or use mock data
  if (data.mock_data) {
    // Use fallback mock data
    setForecastData(data.mock_data);
  }
} else {
  // Normal response
  setForecastData(data);
}

// Check for warnings in metadata
if (data.data?.meta?.warning) {
  console.warn('Warning:', data.data.meta.warning);
}
```

---

## Backend Logs

Check backend console logs for detailed error information:

```
ERROR: External API error - Status: 400
URL: https://aecial-romona-unwrested.ngrok-free.dev/api/run
Error text: {"error": "Invalid source parameter"}
Headers: {...}
```

---

## Quick Checklist

- [ ] Test external API directly with curl
- [ ] Check debug endpoint: `/api/v1/debug/test-external-api`
- [ ] Verify ngrok URL is active
- [ ] Check API key is correct
- [ ] Enable DEBUG mode to see detailed errors
- [ ] Check backend console logs
- [ ] Verify request format matches API expectations

---

## Next Steps

1. **Run the debug endpoint** to see exact error:
   ```
   GET http://localhost:8000/api/v1/debug/test-external-api
   ```

2. **Enable debug mode** to see errors in forecast responses:
   ```
   Set DEBUG=true
   ```

3. **Check backend logs** for detailed error messages

4. **Test external API directly** to verify it's working









