# How to Restart Backend Server

## ⚠️ IMPORTANT: Server Must Be Restarted

The code changes won't take effect until you **restart the backend server**.

## Steps to Restart

### Option 1: If Running in Terminal/PowerShell

1. **Stop the server**: Press `Ctrl+C` in the terminal where the server is running
2. **Start it again**:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 2: If Running as Background Process

1. **Find the process**:
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*uvicorn*"}
   ```

2. **Kill the process**:
   ```powershell
   Stop-Process -Name python -Force
   ```

3. **Restart**:
   ```powershell
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Option 3: Using Task Manager

1. Open Task Manager (Ctrl+Shift+Esc)
2. Find Python processes
3. End the uvicorn process
4. Restart from terminal

## Verify Changes Are Applied

After restarting, check the logs. You should see:
```
INFO: Sending request to https://... with ngrok bypass header
```

Or test the debug endpoint:
```
GET http://localhost:8000/api/v1/debug/test-external-api
```

The request should now include the `ngrok-skip-browser-warning` header.

## If Still Not Working

If the header still doesn't appear after restart:

1. **Check if code was saved**: Verify `backend/app/api/v1/forecast.py` has the header
2. **Clear Python cache**: Delete `__pycache__` folders
3. **Check for syntax errors**: Look for errors in terminal when starting
4. **Try alternative solution**: Use ngrok's query parameter method (see below)

## Alternative: ngrok Query Parameter

If the header method doesn't work, you can also try adding a query parameter to the URL:

```python
EXTERNAL_API_URL = "https://aecial-romona-unwrested.ngrok-free.dev/api/run?ngrok-skip-browser-warning=true"
```

But the header method is preferred and should work once the server is restarted.









