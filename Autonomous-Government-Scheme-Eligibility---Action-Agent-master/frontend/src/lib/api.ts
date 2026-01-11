
const API_BASE_URL = 'http://localhost:8001/api';

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'student' | 'farmer';
  createdAt?: string;
  phone?: string;
}

export interface AuthResponse {
  success: boolean;
  message?: string;
  user?: User;
  error?: string;
}

export interface Scheme {
  scheme_id: string;
  name: string;
  category: string;
  description: string;
  target_groups: string[];
  status?: string;
  relevance_score?: number;
  benefits?: string;
}

export interface SchemeResponse {
  total_schemes: number;
  schemes: Scheme[];
}

export const api = {
  auth: {
    login: async (email: string, password: string): Promise<AuthResponse> => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Login failed');
        }
        return { success: true, user: data.user };
      } catch (error: any) {
        return { success: false, error: error.message };
      }
    },

    signup: async (name: string, email: string, phone: string, password: string): Promise<AuthResponse> => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, phone, password }),
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Signup failed');
        }
        return { success: true, message: data.message };
      } catch (error: any) {
        return { success: false, error: error.message };
      }
    }
  },

  schemes: {
    getAll: async (): Promise<Scheme[]> => {
      try {
        const response = await fetch(`${API_BASE_URL}/v1/schemes`);
        if (!response.ok) throw new Error('Failed to fetch schemes');
        const data = await response.json();
        return data.schemes;
      } catch (error) {
        console.error("Error fetching schemes:", error);
        return [];
      }
    },

    getEligible: async (userId: string, profile: any = {}): Promise<any> => {
      try {
        const response = await fetch(`${API_BASE_URL}/v1/eligible-schemes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, profile })
        });
        if (!response.ok) throw new Error('Failed to fetch eligible schemes');
        return await response.json();
      } catch (error) {
        console.error("Error fetching eligible schemes:", error);
        throw error;
      }
    },
    
    apply: async (userInput: string, userId: string, options: any = {}) => {
        try {
            const response = await fetch(`${API_BASE_URL}/v1/apply-scheme`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_input: userInput,
                    user_id: userId,
                    options
                })
            });
            if (!response.ok) throw new Error('Failed to apply for schemes');
            return await response.json();
        } catch (error) {
            console.error("Error applying for schemes:", error);
            throw error;
        }
    }
  }
};
