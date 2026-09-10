/**
 * Auth Store - Zustand store for authentication state
 */

import { create } from 'zustand';
import { User } from './types';
import { apiClient } from './api-client';

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  initialize: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;

  // Selectors
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,

  initialize: () => {
    if (typeof window === 'undefined') return;

    apiClient.loadToken();
    const token = apiClient.getToken();
    const userStr = localStorage.getItem('auth_user');

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, token });
      } catch (e) {
        console.error('Failed to parse stored user:', e);
        localStorage.removeItem('auth_user');
      }
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.login(email, password);
      localStorage.setItem('auth_user', JSON.stringify(response.user));
      set({
        user: response.user,
        token: response.access_token,
        isLoading: false,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.register(email, password);
      localStorage.setItem('auth_user', JSON.stringify(response.user));
      set({
        user: response.user,
        token: response.access_token,
        isLoading: false,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await apiClient.logout();
      localStorage.removeItem('auth_user');
      set({
        user: null,
        token: null,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      // Still clear local state even if logout call fails
      localStorage.removeItem('auth_user');
      set({
        user: null,
        token: null,
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),

  isAuthenticated: () => {
    const { user, token } = get();
    return !!(user && token);
  },
}));
