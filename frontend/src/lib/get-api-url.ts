/**
 * Get API URL dynamically at runtime
 * This function determines the backend API URL based on the current domain
 * 
 * Priority:
 * 1. NEXT_PUBLIC_API_URL environment variable (if set at build time)
 * 2. Runtime detection based on current domain
 * 3. Fallback to localhost for development
 */

/**
 * Get the backend API URL at runtime
 * This handles cases where NEXT_PUBLIC_API_URL might not be set or needs to be detected dynamically
 */
export function getApiUrl(): string {
  // Check if NEXT_PUBLIC_API_URL is set (baked into build)
  const envApiUrl = process.env.NEXT_PUBLIC_API_URL;
  
  // If NEXT_PUBLIC_API_URL is set and it's not localhost, use it
  // BUT: Check if it's a valid URL (not the old broken one)
  if (envApiUrl && envApiUrl !== 'http://localhost:8000/api/v1') {
    // Check if the URL contains the old broken backend domain
    if (envApiUrl.includes('beauty-aryan-back-production.up.railway.app')) {
      console.error('[API URL] ERROR: NEXT_PUBLIC_API_URL is set to a non-existent backend URL:', envApiUrl);
      console.error('[API URL] This backend service does not exist. Please update NEXT_PUBLIC_API_URL in Railway.');
      console.error('[API URL] Falling back to runtime detection...');
      // Don't use the broken URL, fall through to runtime detection
    } else {
      // Valid URL, use it
      if (typeof window !== 'undefined') {
        console.log('[API URL] Using NEXT_PUBLIC_API_URL:', envApiUrl);
      }
      return envApiUrl;
    }
  }
  
  if (typeof window !== 'undefined') {
    // Client-side: Check if we can detect the backend from the current domain
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // If we're on the custom domain (www.suryadrishti.in or suryadrishti.in)
    if (hostname.includes('suryadrishti.in')) {
      // Try common backend URL patterns for Railway
      // Pattern 1: Backend might be on a subdomain (api.suryadrishti.in)
      // Pattern 2: Backend might be on a different Railway service (needs NEXT_PUBLIC_API_URL)
      // Pattern 3: Backend might be on the same domain with /api path
      
      console.error('[API URL] ERROR: Cannot determine backend URL for custom domain.');
      console.error('[API URL] Current hostname:', hostname);
      console.error('[API URL] NEXT_PUBLIC_API_URL is not set or is invalid.');
      console.error('[API URL] SOLUTION: Set NEXT_PUBLIC_API_URL in Railway frontend service environment variables.');
      console.error('[API URL] Step 1: Go to Railway Dashboard → Backend Service → Settings → Networking');
      console.error('[API URL] Step 2: Copy your backend Railway domain (e.g., your-backend-service.up.railway.app)');
      console.error('[API URL] Step 3: Go to Frontend Service → Variables → Add NEXT_PUBLIC_API_URL');
      console.error('[API URL] Step 4: Set value to: https://your-backend-service.up.railway.app/api/v1');
      console.error('[API URL] Step 5: Redeploy frontend service');
      
      // Try to construct a potential backend URL
      // Remove 'www.' prefix if present to get base domain
      const baseDomain = hostname.replace(/^www\./, '');
      const potentialBackendUrl = `${protocol}//api.${baseDomain}/api/v1`;
      console.warn('[API URL] Attempting fallback URL (this may not work if backend is not on api.suryadrishti.in):', potentialBackendUrl);
      console.warn('[API URL] NOTE: This fallback will only work if you have set up api.suryadrishti.in as a custom domain for your backend.');
      console.warn('[API URL] RECOMMENDED: Set NEXT_PUBLIC_API_URL to your Railway backend URL instead.');
      return potentialBackendUrl;
    }
    
    // If we're on a Railway domain (frontend)
    if (hostname.includes('railway.app')) {
      // For Railway deployments, backend should be set via NEXT_PUBLIC_API_URL
      // If not set, we can't guess it - user must configure it
      console.error('[API URL] ERROR: NEXT_PUBLIC_API_URL is not set for Railway deployment.');
      console.error('[API URL] Current hostname:', hostname);
      console.error('[API URL] SOLUTION: Set NEXT_PUBLIC_API_URL in Railway frontend service environment variables.');
      console.error('[API URL] Go to Railway Dashboard → Frontend Service → Variables → Add NEXT_PUBLIC_API_URL');
      console.error('[API URL] Value should be: https://your-backend-service.railway.app/api/v1');
      
      // Return localhost as fallback (won't work in production, but at least won't crash)
      return 'http://localhost:8000/api/v1';
    }
    
    // Localhost development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return envApiUrl || 'http://localhost:8000/api/v1';
    }
  }
  
  // Server-side or fallback
  return envApiUrl || 'http://localhost:8000/api/v1';
}

/**
 * Get API base URL without /api/v1 suffix
 */
export function getApiBaseUrl(): string {
  const apiUrl = getApiUrl();
  return apiUrl.replace('/api/v1', '');
}

/**
 * Log the API URL being used (for debugging)
 */
export function logApiUrl(): void {
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    const apiUrl = getApiUrl();
    console.log('[API URL] Using backend URL:', apiUrl);
    console.log('[API URL] Current hostname:', window.location.hostname);
    console.log('[API URL] NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL || 'not set');
  }
}

