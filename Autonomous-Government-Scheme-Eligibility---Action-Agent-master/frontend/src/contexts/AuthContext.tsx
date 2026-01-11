import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

export type UserRole = 'student' | 'farmer';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: string;
  phone?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string, role: UserRole) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const CURRENT_USER_KEY = 'govscheme_current_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const storedUser = localStorage.getItem(CURRENT_USER_KEY);
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(CURRENT_USER_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const result = await api.auth.login(email, password);
      
      if (result.success && result.user) {
        // Map backend user to frontend user model if necessary
        // Assuming backend returns a compatible user object or we cast it
        const userRole = result.user.role || 'student'; // Fallback
        const user: User = {
            ...result.user,
            role: userRole as UserRole
        };
        
        setUser(user);
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
        return { success: true };
      }
      return { success: false, error: result.error || 'Login failed' };
    } catch (error: any) {
      return { success: false, error: error.message || 'An error occurred' };
    }
  };

  const register = async (
    name: string,
    email: string,
    password: string,
    role: UserRole
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      // For now, using a dummy phone number since the UI doesn't ask for it yet in all flows
      // or we update the UI later. The backend requires 'phone'.
      const phone = "0000000000"; 
      
      const result = await api.auth.signup(name, email, phone, password);
      
      if (result.success) {
        // Auto-login after signup if desired, or just return success
        // For now, let's auto-login or ask user to login.
        // The backend signup doesn't return the user object, so we might need to login.
        // Let's just return success and let the UI redirect to login or dashboard if we implement auto-login.
        // The current UI redirects to Dashboard on success, but we haven't set the user state!
        
        // If the backend doesn't return the user, we can't set the state effectively without logging in.
        // We'll perform a background login or require the user to login.
        // To match the existing flow (navigate to dashboard), we need to set the user.
        
        // OPTION: Immediately call login
        const loginResult = await login(email, password);
        return loginResult;
      }
      return { success: false, error: result.error || 'Registration failed' };
    } catch (error: any) {
      return { success: false, error: error.message || 'An error occurred' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(CURRENT_USER_KEY);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
