/**
 * API Configuration
 * 
 * This file centralizes all API endpoints and configuration.
 * Environment variables are loaded at BUILD TIME and cannot be changed at runtime.
 * 
 * In development: Use .env.local with your local settings
 * In production (Render): Uses REACT_APP_API_URL set from RENDER_EXTERNAL_URL
 */

// Base API URL from environment or fallback to current host
// On Render, REACT_APP_API_URL will be set from RENDER_EXTERNAL_URL during build
export const API_URL = process.env.REACT_APP_API_URL || window.location.origin;

// API Endpoints
export const API_ENDPOINTS = {
  LOGIN: process.env.REACT_APP_LOGIN_ENDPOINT || '/login',
  VERIFY_TOKEN: process.env.REACT_APP_VERIFY_TOKEN_ENDPOINT || '/verify-token',
  SUBMIT: process.env.REACT_APP_SUBMIT_ENDPOINT || '/submit-product',
  STATUS: process.env.REACT_APP_STATUS_ENDPOINT || '/processing-status',
};

// Authentication Configuration
export const AUTH_CONFIG = {
  TOKEN_KEY: process.env.REACT_APP_TOKEN_STORAGE_KEY || 'token',
  JWT_EXPIRATION_HOURS: parseInt(process.env.REACT_APP_JWT_EXPIRATION_HOURS || '1', 10),
};

// UI Configuration
export const UI_CONFIG = {
  MAX_FILE_SIZE: parseInt(process.env.REACT_APP_MAX_FILE_SIZE || '10485760', 10), // 10MB
  MAX_IMAGES: parseInt(process.env.REACT_APP_MAX_IMAGES || '5', 10),
};

// Feature Flags
export const FEATURES = {
  DEBUG: process.env.REACT_APP_DEBUG === 'true',
  SHOW_IMAGE_PREVIEW: process.env.REACT_APP_SHOW_IMAGE_PREVIEW !== 'false',
  ENABLE_WARNING_VALIDATION: process.env.REACT_APP_ENABLE_WARNING_VALIDATION !== 'false',
};

/**
 * Build-time Configuration Check
 * Logs configuration on app startup in development
 */
if (process.env.NODE_ENV === 'development' && FEATURES.DEBUG) {
  console.group('🔧 API Configuration');
  console.log('API URL:', API_URL);
  console.log('Endpoints:', API_ENDPOINTS);
  console.log('Auth Config:', AUTH_CONFIG);
  console.log('UI Config:', UI_CONFIG);
  console.log('Features:', FEATURES);
  console.groupEnd();
}

export default {
  API_URL,
  API_ENDPOINTS,
  AUTH_CONFIG,
  UI_CONFIG,
  FEATURES,
};
