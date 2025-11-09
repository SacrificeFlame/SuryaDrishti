# Railway Build Debugging Guide

## Current Issue
The frontend build is failing on Railway with "Build failed because of webpack errors" but the actual error is not shown.

## Debug Steps Added

I've added debug commands to `frontend/nixpacks.toml` that will:
1. Show the current working directory (`pwd`)
2. List all files in the root (`ls -la`)
3. Verify `src/`, `src/lib/`, and `src/types/` directories exist
4. Verify `tsconfig.json` and `next.config.js` files exist
5. Run the build with full error output (`2>&1`)

## What to Check in Railway

### 1. Service Configuration
- Go to your Railway project dashboard
- Click on the **Frontend** service
- Go to **Settings** tab
- Verify **Root Directory** is set to `frontend`
  - If not set, Railway might be building from the project root instead of `frontend/`
  - This would cause files to not be found

### 2. Build Logs
After the next deployment, check the build logs for:
- Output from `pwd` - should show `/app` or similar
- Output from `ls -la` - should show `src/`, `package.json`, `tsconfig.json`, etc.
- Any "NOT FOUND" messages from the debug commands
- The actual webpack error (should now be visible with `2>&1`)

### 3. Environment Variables
- Verify `NEXT_PUBLIC_API_URL` is set (if needed)
- Check that `NODE_ENV=production` is set (handled by nixpacks.toml)

## Common Issues

### Issue 1: Root Directory Not Set
**Symptom**: Files like `tsconfig.json` or `src/` not found
**Fix**: Set Root Directory to `frontend` in Railway service settings

### Issue 2: Files Not Copied
**Symptom**: Debug commands show files missing
**Fix**: Check `.dockerignore` or `.railwayignore` - they might be excluding necessary files

### Issue 3: Path Alias Resolution
**Symptom**: "Module not found: Can't resolve '@/lib/api-client'"
**Fix**: 
- Verify `tsconfig.json` has `"baseUrl": "."` and `"paths": { "@/*": ["./src/*"] }`
- Verify `next.config.js` has webpack alias configuration
- Check that `src/lib/api-client.ts` actually exists

## Next Steps

1. **Check Railway Service Settings**: Verify Root Directory is `frontend`
2. **Deploy Again**: The debug output will show what's happening
3. **Review Build Logs**: Look for the debug output and actual error messages
4. **Share Logs**: If still failing, share the full build log output

## Expected Build Log Output

```
/app
total XX
drwxr-xr-x ...
-rw-r--r-- ... package.json
-rw-r--r-- ... tsconfig.json
-rw-r--r-- ... next.config.js
drwxr-xr-x ... src
...

src directory exists
src/lib directory exists
src/types directory exists
tsconfig.json exists
next.config.js exists
> next build
...
```

If any of these show "NOT FOUND", that's the issue.

