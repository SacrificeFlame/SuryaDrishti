/**
 * Forecast Error Handler
 * Provides consistent error handling for forecast API calls
 */

import { isNetworkError, isDNSError, getNetworkErrorMessage, logNetworkError } from './networkErrorHandler';

// Import getApiUrl - conditional import to avoid SSR issues
// This will be undefined on server-side, which is fine
let getApiUrlFn: (() => string) | undefined;

if (typeof window !== 'undefined') {
  try {
    // Dynamic import to avoid SSR issues - but we'll call it synchronously in the function
    // Since getApiUrl() itself is synchronous, we can import the module
    const apiUrlModule = require('@/lib/get-api-url');
    getApiUrlFn = apiUrlModule.getApiUrl;
  } catch (e) {
    // Ignore import errors - will fall back to undefined API URL
  }
}

export interface ForecastError {
  message: string;
  type: 'network' | 'api' | 'validation' | 'unknown';
  statusCode?: number;
  retryable: boolean;
}

/**
 * Handle forecast API errors and return structured error information
 */
export function handleForecastError(error: unknown): ForecastError {
  // Network errors (connection issues) - use improved network error handler
  if (isNetworkError(error) || isDNSError(error)) {
    // Get the API URL for better error messages
    let apiUrl: string | undefined;
    try {
      if (getApiUrlFn && typeof window !== 'undefined') {
        apiUrl = getApiUrlFn();
      }
    } catch (e) {
      // Ignore errors when getting API URL
    }
    
    // Log detailed error information
    logNetworkError(error, apiUrl);
    
    return {
      message: getNetworkErrorMessage(error, apiUrl),
      type: 'network',
      retryable: true,
    };
  }

  if (error instanceof Error) {
    // 404 - Not Found
    if (error.message.includes('404') || error.message.includes('not found')) {
      return {
        message: 'Microgrid not found. Please check the microgrid ID.',
        type: 'validation',
        retryable: false,
      };
    }

    // 500 - Server Error
    if (error.message.includes('500') || error.message.includes('Internal Server Error')) {
      return {
        message: 'Server error. Please try again later.',
        type: 'api',
        statusCode: 500,
        retryable: true,
      };
    }

    // 400 - Bad Request
    if (error.message.includes('400') || error.message.includes('Bad Request')) {
      return {
        message: 'Invalid request parameters. Please check your input.',
        type: 'validation',
        statusCode: 400,
        retryable: false,
      };
    }

    // Timeout errors
    if (error.message.includes('timeout') || error.message.includes('Timeout')) {
      return {
        message: 'Request timed out. The server is taking too long to respond.',
        type: 'network',
        retryable: true,
      };
    }

    // Generic API errors
    return {
      message: error.message,
      type: 'api',
      retryable: true,
    };
  }

  // Unknown errors
  return {
    message: 'An unexpected error occurred',
    type: 'unknown',
    retryable: true,
  };
}

/**
 * Check if an error is retryable
 */
export function isRetryableError(error: ForecastError): boolean {
  return error.retryable && error.type !== 'validation';
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: ForecastError): string {
  switch (error.type) {
    case 'network':
      return 'Connection error. Please check your internet connection and try again.';
    case 'validation':
      return error.message;
    case 'api':
      return error.message || 'An error occurred while fetching data.';
    default:
      return 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Get error icon/color for UI
 */
export function getErrorStyle(error: ForecastError): {
  color: string;
  bgColor: string;
  icon: string;
} {
  switch (error.type) {
    case 'network':
      return {
        color: 'text-yellow-800',
        bgColor: 'bg-yellow-50 border-yellow-200',
        icon: '⚠️',
      };
    case 'validation':
      return {
        color: 'text-red-800',
        bgColor: 'bg-red-50 border-red-200',
        icon: '❌',
      };
    case 'api':
      return {
        color: 'text-orange-800',
        bgColor: 'bg-orange-50 border-orange-200',
        icon: '⚠️',
      };
    default:
      return {
        color: 'text-gray-800',
        bgColor: 'bg-gray-50 border-gray-200',
        icon: '❓',
      };
  }
}











