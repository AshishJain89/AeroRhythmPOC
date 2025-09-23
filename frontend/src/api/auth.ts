import apiClient, { apiRequest, AuthToken } from './apiClient';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  permissions: string[];
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    return apiRequest(() =>
      apiClient.post<AuthToken>('/auth/token', credentials)
    );
  },

  async getCurrentUser(): Promise<User> {
    return apiRequest(() => apiClient.get<User>('/auth/me'));
  },

  async refreshToken(): Promise<AuthToken> {
    return apiRequest(() => apiClient.post<AuthToken>('/auth/refresh'));
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Handle logout even if API call fails
    }
  }
};
