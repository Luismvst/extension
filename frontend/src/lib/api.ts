/**
 * Centralized API client for the frontend.
 * 
 * This module provides a unified way to make API calls with:
 * - Proper base URL configuration
 * - Request/response interceptors
 * - Error handling
 * - AbortController support for cancellation
 */

export const API_BASE = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8080';

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: Response
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Centralized fetch function with proper error handling and base URL.
 */
export const apiFetch = async <T = any>(
  path: string,
  init: RequestInit = {},
  signal?: AbortSignal
): Promise<ApiResponse<T>> => {
  const url = `${API_BASE}${path}`;
  
  try {
    const response = await fetch(url, {
      ...init,
      signal,
      headers: {
        'Content-Type': 'application/json',
        ...init.headers,
      },
    });

    let data: T | undefined;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    }

    if (!response.ok) {
      throw new ApiError(
        (data as any)?.error || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        response
      );
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('Request was cancelled', 0);
    }
    
    throw new ApiError(
      error instanceof Error ? error.message : 'Unknown error occurred',
      0
    );
  }
};

/**
 * API methods for different endpoints.
 */
export const api = {
  // Auth endpoints
  auth: {
    login: (email: string, password: string, signal?: AbortSignal) =>
      apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
        signal,
      }),
    
    me: (token: string, signal?: AbortSignal) =>
      apiFetch('/auth/me', {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
        signal,
      }),
    
    validate: (token: string, signal?: AbortSignal) =>
      apiFetch('/auth/validate', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        signal,
      }),
  },

  // Health endpoint
  health: (signal?: AbortSignal) =>
    apiFetch('/api/v1/health', { signal }),

  // Orders endpoints
  orders: {
    fetch: (signal?: AbortSignal) =>
      apiFetch('/api/v1/orchestrator/fetch-orders', {
        method: 'POST',
        signal,
      }),
    
    postToCarrier: (carrier: string, signal?: AbortSignal) =>
      apiFetch(`/api/v1/orchestrator/post-to-carrier`, {
        method: 'POST',
        body: JSON.stringify({ carrier }),
        signal,
      }),
    
    pushTracking: (signal?: AbortSignal) =>
      apiFetch('/api/v1/orchestrator/push-tracking-to-mirakl', {
        method: 'POST',
        signal,
      }),
    
    getView: (signal?: AbortSignal) =>
      apiFetch('/api/v1/orchestrator/orders-view', { signal }),
  },

  // Logs endpoints
  logs: {
    operations: (signal?: AbortSignal) =>
      apiFetch('/api/v1/logs/operations', { signal }),
    
    ordersView: (signal?: AbortSignal) =>
      apiFetch('/api/v1/logs/orders_view', { signal }),
    
    export: (filename: string, signal?: AbortSignal) =>
      apiFetch(`/api/v1/exports/${filename}.csv`, { signal }),
  },
};

/**
 * Create an AbortController with timeout.
 */
export const createTimeoutController = (timeoutMs: number = 12000): AbortController => {
  const controller = new AbortController();
  
  setTimeout(() => {
    controller.abort();
  }, timeoutMs);
  
  return controller;
};

/**
 * Utility to handle API errors in UI components.
 */
export const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    if (error.status === 0) {
      return 'Request was cancelled or network error occurred';
    }
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};
