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
    
    // If we're on the custom domain (www.suryadrishti.in or suryadrishti.in)
    if (hostname.includes('suryadrishti.in')) {
      console.error('═══════════════════════════════════════════════════════════');
      console.error('🚨 BACKEND URL CONFIGURATION ERROR 🚨');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('');
      console.error('The frontend cannot connect to the backend because:');
      console.error('1. NEXT_PUBLIC_API_URL is set to a non-existent backend URL');
      console.error('2. OR NEXT_PUBLIC_API_URL is not set correctly');
      console.error('');
      console.error('Current hostname:', hostname);
      console.error('NEXT_PUBLIC_API_URL:', envApiUrl || 'NOT SET');
      console.error('');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('📋 HOW TO FIX THIS (STEP BY STEP):');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('');
      console.error('STEP 1: Find your backend Railway URL');
      console.error('  → Go to Railway Dashboard: https://railway.app');
      console.error('  → Open your BACKEND service (the one running Python/FastAPI)');
      console.error('  → Go to: Settings → Networking → Public Networking');
      console.error('  → Copy the Railway domain (e.g., my-backend-service.up.railway.app)');
      console.error('');
      console.error('STEP 2: Update NEXT_PUBLIC_API_URL in Railway');
      console.error('  → Go to Railway Dashboard');
      console.error('  → Open your FRONTEND service (the one running Next.js)');
      console.error('  → Go to: Variables tab');
      console.error('  → Find or add: NEXT_PUBLIC_API_URL');
      console.error('  → Set value to: https://YOUR-BACKEND-SERVICE.up.railway.app/api/v1');
      console.error('  → Replace YOUR-BACKEND-SERVICE with your actual backend domain');
      console.error('');
      console.error('STEP 3: Redeploy Frontend');
      console.error('  → After saving the variable, Railway will auto-redeploy');
      console.error('  → OR manually trigger a redeploy from the Deployments tab');
      console.error('  → Wait for deployment to complete');
      console.error('');
      console.error('STEP 4: Verify');
      console.error('  → Refresh this page');
      console.error('  → Check browser console - should see: [API URL] Using NEXT_PUBLIC_API_URL: https://...');
      console.error('  → Verify no more ERR_NAME_NOT_RESOLVED errors');
      console.error('');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('⚠️  IMPORTANT: You MUST redeploy after changing NEXT_PUBLIC_API_URL');
      console.error('   Next.js bakes environment variables into the build at build time.');
      console.error('   Changing the variable alone is not enough - you must rebuild/redeploy!');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('');
      
      // Don't use fallback URL - it doesn't exist and causes confusion
      // Instead, return a URL that will fail gracefully with a clear error
      // This forces the user to fix the configuration
      console.error('❌ NOT using fallback URL (api.suryadrishti.in) - it does not exist.');
      console.error('❌ Please set NEXT_PUBLIC_API_URL to your actual Railway backend URL and redeploy.');
      console.error('');
      
      // Return a URL that will fail immediately with DNS error (not CORS)
      // Using a non-existent domain that will definitely fail DNS resolution
      return 'https://backend-url-not-configured-invalid-domain-12345.invalid/api/v1';
    }
    
    // If we're on a Railway domain (frontend)
    if (hostname.includes('railway.app')) {
      console.error('═══════════════════════════════════════════════════════════');
      console.error('🚨 BACKEND URL NOT CONFIGURED 🚨');
      console.error('═══════════════════════════════════════════════════════════');
      console.error('');
      console.error('Current hostname:', hostname);
      console.error('NEXT_PUBLIC_API_URL:', envApiUrl || 'NOT SET');
      console.error('');
      console.error('SOLUTION:');
      console.error('1. Go to Railway Dashboard → Frontend Service → Variables');
      console.error('2. Add NEXT_PUBLIC_API_URL');
      console.error('3. Set to: https://your-backend-service.railway.app/api/v1');
      console.error('4. Redeploy frontend service');
      console.error('');
      console.error('═══════════════════════════════════════════════════════════');
      
      // Return a URL that will fail immediately with DNS error (not CORS)
      // Using a non-existent domain that will definitely fail DNS resolution
      return 'https://backend-url-not-configured-invalid-domain-12345.invalid/api/v1';
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

