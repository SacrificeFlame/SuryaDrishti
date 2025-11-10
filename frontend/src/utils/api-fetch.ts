/**
 * API Fetch Utility
 * Wraps fetch() with automatic network error handling and better error messages
 */

import { isNetworkError, isDNSError, getNetworkErrorMessage, logNetworkError } from './networkErrorHandler';

/**
 * Fetch with automatic network error handling
 * This wrapper catches network errors and provides actionable error messages
 */
export async function fetchWithErrorHandling(
  url: string,
  options?: RequestInit
): Promise<Response> {
  try {
    const response = await fetch(url, options);
    return response;
  } catch (error) {
    // Handle network errors (DNS resolution, connection refused, etc.)
    if (isNetworkError(error) || isDNSError(error)) {
      logNetworkError(error, url);
      const errorMessage = getNetworkErrorMessage(error, url);
      throw new Error(errorMessage);
    }
    // Re-throw other errors as-is
    throw error;
  }
}

/**
 * Fetch JSON with automatic error handling
 * Convenience wrapper that also handles JSON parsing
 */
export async function fetchJson<T = any>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetchWithErrorHandling(url, options);
  
  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }
  
  return response.json();
}

