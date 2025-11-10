# Fixing ngrok ERR_NGROK_8012 Error

## Problem
The external API is behind ngrok, and ngrok is showing a browser warning page (ERR_NGROK_8012) which blocks the request.

## Solution Applied
Added the `ngrok-skip-browser-warning: true` header to bypass ngrok's browser warning page.

## What Changed
Updated both endpoints to include the bypass header:
- `/api/v1/forecast/schedule`
- `/api/v1/debug/test-external-api`

## Alternative Solutions

### Option 1: Use ngrok's bypass header (✅ Applied)
Add header: `ngrok-skip-browser-warning: true`

### Option 2: Configure ngrok to skip browser warning
When starting ngrok, use:
```bash
ngrok http 8000 --request-header-add "ngrok-skip-browser-warning:true"
```

### Option 3: Use ngrok's static domain (if available)
Static domains don't show browser warnings.

### Option 4: Upgrade ngrok plan
Paid ngrok plans don't show browser warnings.

## Testing
After the fix, test again:
```
GET http://localhost:8000/api/v1/debug/test-external-api
```

The request should now bypass the ngrok warning page and reach your actual API.

## If Still Not Working

1. **Check if ngrok URL is still active**
   - ngrok free URLs expire when the session ends
   - Verify the ngrok tunnel is running

2. **Check if the actual API endpoint is correct**
   - Verify `/api/run` is the correct endpoint
   - Test the API directly (if possible)

3. **Check API key**
   - Verify the API key is correct
   - Check if the API expects a different header format

4. **Check request body format**
   - Verify `{"source": "hybrid"}` is the expected format
   - Check if the API expects different parameters









