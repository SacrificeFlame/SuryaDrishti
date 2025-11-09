# Environment Variables Configuration

This document describes all environment variables needed for the SuryaDrishti application.

## Backend Environment Variables

### Database Configuration

```bash
# SQLite (default) - no configuration needed
# Database file: backend/suryादrishti.db

# PostgreSQL (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/suryादrishti
```

### External API Configuration

```bash
# External Forecast API (optional)
EXTERNAL_API_URL=http://127.0.0.1:8000/api/run
EXTERNAL_API_KEY=your_api_key_here
```

### Twilio SMS Configuration (for notifications)

```bash
# Twilio Account SID (get from https://www.twilio.com/console)
TWILIO_ACCOUNT_SID=your_account_sid_here

# Twilio Auth Token (get from https://www.twilio.com/console)
TWILIO_AUTH_TOKEN=your_auth_token_here

# Twilio Phone Number (format: +1234567890)
TWILIO_FROM_NUMBER=+1234567890
```

**Note:** To use SMS notifications:
1. Sign up for a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number or use a trial number
4. Add these variables to your `.env` file in the `backend/` directory

### Application Settings

```bash
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging Level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Frontend Environment Variables

### API Configuration

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Note:** Create a `.env.local` file in the `frontend/` directory with this variable.

## Setting Up Environment Variables

### Backend

1. Create a `.env` file in the `backend/` directory:
```bash
cd backend
touch .env
```

2. Add your environment variables:
```bash
# Example .env file
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890
EXTERNAL_API_URL=http://127.0.0.1:8000/api/run
EXTERNAL_API_KEY=your_api_key_here
```

3. The backend will automatically load these variables using `python-dotenv`.

### Frontend

1. Create a `.env.local` file in the `frontend/` directory:
```bash
cd frontend
touch .env.local
```

2. Add your environment variables:
```bash
# Example .env.local file
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Restart the Next.js development server for changes to take effect.

## Required vs Optional

### Required Variables
- None (all have defaults or are optional)

### Optional but Recommended
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` - Required for SMS notifications
- `NEXT_PUBLIC_API_URL` - Required if backend is not on `http://localhost:8000`

### Optional
- `EXTERNAL_API_URL`, `EXTERNAL_API_KEY` - Only if using external forecast API
- `DATABASE_URL` - Only if using PostgreSQL instead of SQLite
- `CORS_ORIGINS` - Only if frontend is on a different origin
- `LOG_LEVEL` - Only if you want to change logging verbosity

## Security Notes

⚠️ **Never commit `.env` or `.env.local` files to version control!**

These files contain sensitive information like API keys and tokens. Always add them to `.gitignore`.

Example `.gitignore` entries:
```
.env
.env.local
.env.*.local
```

## Testing Configuration

To test if your environment variables are loaded correctly:

### Backend
```python
# In Python shell or script
from app.core.config import settings
print(f"Twilio Account SID: {settings.TWILIO_ACCOUNT_SID}")
```

### Frontend
```typescript
// In browser console or component
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
```

## Troubleshooting

### Backend can't find environment variables
- Make sure `.env` file is in the `backend/` directory
- Check that variable names match exactly (case-sensitive)
- Restart the backend server after adding/changing variables

### Frontend can't connect to backend
- Check that `NEXT_PUBLIC_API_URL` is set correctly
- Make sure the backend is running on the specified port
- Check browser console for CORS errors

### SMS notifications not working
- Verify Twilio credentials are correct
- Check that phone numbers are in E.164 format (+1234567890)
- Check backend logs for Twilio API errors
- Ensure you have sufficient Twilio credits

