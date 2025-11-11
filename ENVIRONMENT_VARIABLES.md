# Environment Variables Guide

Complete reference for all environment variables used in SuryaDrishti.

## Backend Environment Variables

### Required Variables

#### `DATABASE_URL`
- **Description:** PostgreSQL database connection string
- **Format:** `postgresql://user:password@host:port/database`
- **Note:** Automatically set by Railway when you add PostgreSQL database
- **Example:** `postgresql://postgres:password@containers-us-west-123.railway.app:5432/railway`

#### `ALLOWED_ORIGINS`
- **Description:** Comma-separated list of allowed CORS origins
- **Required:** Yes
- **Example:** `https://www.suryadrishti.in,https://suryadrishti.in,https://your-frontend.railway.app`

#### `FRONTEND_URLS`
- **Description:** Comma-separated list of frontend URLs (alternative to ALLOWED_ORIGINS)
- **Required:** Yes (if not using ALLOWED_ORIGINS)
- **Example:** `https://www.suryadrishti.in,https://suryadrishti.in`

#### `SECRET_KEY`
- **Description:** Secret key for JWT token generation
- **Required:** Yes
- **Generate:** Use a strong random string (32+ characters)
- **Example:** `your-super-secret-key-change-in-production-12345`

### Optional Variables

#### `TWILIO_ACCOUNT_SID`
- **Description:** Twilio account SID for SMS notifications
- **Required:** No
- **Example:** `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `TWILIO_AUTH_TOKEN`
- **Description:** Twilio authentication token
- **Required:** No (if using Twilio)
- **Example:** `your-twilio-auth-token`

#### `TWILIO_FROM_NUMBER`
- **Description:** Twilio phone number for sending SMS
- **Required:** No (if using Twilio)
- **Format:** E.164 format with country code
- **Example:** `+1234567890`

#### `DEBUG`
- **Description:** Enable debug mode
- **Default:** `False`
- **Values:** `True` or `False`

#### `ENVIRONMENT`
- **Description:** Environment name
- **Default:** `development`
- **Values:** `development`, `production`, `staging`

## Frontend Environment Variables

### Required Variables

#### `NEXT_PUBLIC_API_URL`
- **Description:** Backend API URL (must include `/api/v1` suffix)
- **Required:** Yes
- **Format:** `https://your-backend-service.up.railway.app/api/v1`
- **Current Value:** `https://beauty-aryan-back-production.up.railway.app/api/v1`
- **Important:** 
  - Must start with `https://`
  - Must end with `/api/v1`
  - Changes require frontend redeployment to take effect

### How Next.js Environment Variables Work

- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- These variables are baked into the build at build time
- Changing the variable in Railway alone is NOT enough - you MUST redeploy
- Variables are accessible via `process.env.NEXT_PUBLIC_API_URL`

## Setting Variables in Railway

### Backend Service
1. Go to Railway Dashboard
2. Open your backend service
3. Go to **Variables** tab
4. Click **New Variable**
5. Enter variable name and value
6. Click **Save**
7. Railway will automatically redeploy

### Frontend Service
1. Go to Railway Dashboard
2. Open your frontend service
3. Go to **Variables** tab
4. Click **New Variable**
5. Enter variable name and value
6. Click **Save**
7. **Important:** Manually trigger a redeploy for `NEXT_PUBLIC_*` variables

## Example Configuration

### Backend Service Variables
```env
DATABASE_URL=postgresql://... (auto-set)
ALLOWED_ORIGINS=https://www.suryadrishti.in,https://suryadrishti.in
FRONTEND_URLS=https://www.suryadrishti.in,https://suryadrishti.in
SECRET_KEY=your-secret-key-here
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### Frontend Service Variables
```env
NEXT_PUBLIC_API_URL=https://beauty-aryan-back-production.up.railway.app/api/v1
```

## Troubleshooting

### Variable Not Working
1. **Check variable name:** Must match exactly (case-sensitive)
2. **Check variable value:** No extra spaces or quotes
3. **Redeploy service:** Changes require redeployment
4. **Check logs:** Verify variable is being read correctly

### NEXT_PUBLIC_API_URL Not Updating
1. **Redeploy frontend:** Next.js bakes variables at build time
2. **Clear browser cache:** Old builds may be cached
3. **Check build logs:** Verify variable is included in build
4. **Verify format:** Must be valid URL with `/api/v1` suffix

### CORS Errors
1. **Check ALLOWED_ORIGINS:** Must include your frontend domain
2. **Check FRONTEND_URLS:** Alternative way to set allowed origins
3. **Redeploy backend:** CORS changes require backend redeployment
4. **Verify format:** Comma-separated, no spaces around commas

## Security Best Practices

1. **Never commit secrets:** Use environment variables, not hardcoded values
2. **Use strong SECRET_KEY:** Generate a random 32+ character string
3. **Rotate secrets regularly:** Change SECRET_KEY periodically
4. **Limit ALLOWED_ORIGINS:** Only include domains you own
5. **Use HTTPS:** Always use `https://` in production

## Generating SECRET_KEY

### Python
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Node.js
```javascript
require('crypto').randomBytes(32).toString('base64url')
```

### Online
Use a secure random string generator (32+ characters)

## Need Help?

- Check Railway service logs
- Verify variable names and values
- Test backend API directly
- Check browser console for errors
- Review deployment guide for setup instructions
