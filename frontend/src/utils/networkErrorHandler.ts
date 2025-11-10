/**
 * Network Error Handler
 * Provides utilities for handling network errors, especially backend connection issues
 */

export interface NetworkErrorInfo {
  message: string;
  type: 'connection' | 'timeout' | 'dns' | 'unknown';
  actionable: boolean;
  solution?: string;
}

/**
 * Check if an error is a network/DNS resolution error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    return (
      error.message.includes('fetch') ||
      error.message.includes('Failed to fetch') ||
      error.message.includes('NetworkError') ||
      error.message.includes('ERR_NAME_NOT_RESOLVED') ||
      error.message.includes('ERR_CONNECTION_REFUSED') ||
      error.message.includes('ERR_INTERNET_DISCONNECTED')
    );
  }
  
  if (error instanceof Error) {
    return (
      error.message.includes('NetworkError') ||
      error.message.includes('ERR_NAME_NOT_RESOLVED') ||
      error.message.includes('ERR_CONNECTION_REFUSED') ||
      error.message.includes('ERR_INTERNET_DISCONNECTED') ||
      error.message.includes('Failed to fetch')
    );
  }
  
  return false;
}

/**
 * Check if an error is a DNS resolution error (backend URL cannot be resolved)
 */
export function isDNSError(error: unknown): boolean {
  if (error instanceof TypeError || error instanceof Error) {
    const message = error.message.toLowerCase();
    return (
      message.includes('err_name_not_resolved') ||
      message.includes('getaddrinfo enotfound') ||
      message.includes('dns') ||
      (message.includes('failed to fetch') && message.includes('resolve'))
    );
  }
  return false;
}

/**
 * Handle network errors and provide actionable information
 */
export function handleNetworkError(error: unknown, apiUrl?: string): NetworkErrorInfo {
  // Check if it's a DNS/resolution error
  if (isDNSError(error)) {
    return {
      message: 'Cannot connect to backend server. The backend URL cannot be resolved.',
      type: 'dns',
      actionable: true,
      solution: `
BACKEND URL CONFIGURATION ERROR

The frontend cannot connect to the backend because the backend URL is invalid or not set.

CURRENT API URL: ${apiUrl || 'unknown'}

SOLUTION:
1. Go to Railway Dashboard (https://railway.app)
2. Open your Frontend Service
3. Go to Variables tab
4. Add or update NEXT_PUBLIC_API_URL
5. Set it to your backend Railway URL: https://your-backend-service.up.railway.app/api/v1
6. Redeploy the frontend service

To find your backend URL:
1. Go to Railway Dashboard
2. Open your Backend Service
3. Go to Settings → Networking
4. Copy the Railway domain (e.g., your-backend.up.railway.app)
5. Use: https://your-backend.up.railway.app/api/v1

NOTE: Make sure your backend service is running and accessible.
      `.trim(),
    };
  }
  
  // Check if it's a connection refused error
  if (error instanceof Error && error.message.includes('ERR_CONNECTION_REFUSED')) {
    return {
      message: 'Connection refused. The backend server is not running or not accessible.',
      type: 'connection',
      actionable: true,
      solution: `
BACKEND CONNECTION ERROR

The frontend cannot connect to the backend server.

POSSIBLE CAUSES:
1. Backend service is not running
2. Backend URL is incorrect
3. Backend is blocking connections
4. Network firewall is blocking the connection

SOLUTION:
1. Check if your backend service is running in Railway
2. Verify the backend URL is correct in NEXT_PUBLIC_API_URL
3. Check backend logs for errors
4. Ensure backend is listening on the correct port
      `.trim(),
    };
  }
  
  // Check if it's a general network error
  if (isNetworkError(error)) {
    return {
      message: 'Network error. Cannot connect to backend server.',
      type: 'connection',
      actionable: true,
      solution: `
NETWORK ERROR

The frontend cannot connect to the backend server.

POSSIBLE CAUSES:
1. Backend URL is incorrect or not set
2. Backend service is down
3. Network connectivity issue
4. CORS configuration issue

SOLUTION:
1. Verify NEXT_PUBLIC_API_URL is set correctly in Railway
2. Check if backend service is running
3. Test backend URL directly in browser
4. Check browser console for CORS errors
      `.trim(),
    };
  }
  
  // Unknown error
  return {
    message: error instanceof Error ? error.message : 'Unknown network error',
    type: 'unknown',
    actionable: false,
  };
}

/**
 * Log network error with actionable solution
 */
export function logNetworkError(error: unknown, apiUrl?: string): void {
  const errorInfo = handleNetworkError(error, apiUrl);
  
  console.error('[Network Error]', errorInfo.message);
  console.error('[Network Error Type]', errorInfo.type);
  
  if (errorInfo.actionable && errorInfo.solution) {
    console.error('[Network Error Solution]', errorInfo.solution);
    console.error('[Current API URL]', apiUrl || 'not set');
  }
  
  if (error instanceof Error) {
    console.error('[Error Details]', error);
  }
}

/**
 * Get user-friendly error message for network errors
 */
export function getNetworkErrorMessage(error: unknown, apiUrl?: string): string {
  const errorInfo = handleNetworkError(error, apiUrl);
  
  if (errorInfo.type === 'dns') {
    return 'Backend URL cannot be resolved. Please configure NEXT_PUBLIC_API_URL in Railway.';
  }
  
  if (errorInfo.type === 'connection') {
    return 'Cannot connect to backend server. Please check if the backend is running and the URL is correct.';
  }
  
  return errorInfo.message;
}

