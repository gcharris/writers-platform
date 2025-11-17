import { create } from 'zustand';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('auth_token'),
  isAuthenticated: !!localStorage.getItem('auth_token'),

  login: (token: string, user: User) => {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  setUser: (user: User) => {
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },
}));
