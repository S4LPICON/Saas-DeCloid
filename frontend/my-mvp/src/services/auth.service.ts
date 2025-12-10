import { apiClient, API_BASE_URL } from '../config/api.config';
import type {
  LoginCredentials,
  AuthTokens,
  RefreshTokenResponse,
  UserInfo,
} from '../types/auth.types';
import axios from 'axios';

export const authService = {
  /**
   * Inicia sesión con username y password
   */
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await axios.post<AuthTokens>(
      `${API_BASE_URL}/api/v1/auth/login/`,
      credentials
    );
    return response.data;
  },

  /**
   * Cierra sesión e invalida el refresh token
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await apiClient.post('/api/v1/auth/logout/', {
          refresh: refreshToken,
        });
      } catch (error) {
        console.error('Error al cerrar sesión:', error);
      }
    }
    // Limpiar tokens del localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  /**
   * Obtiene la información del usuario autenticado
   */
  async getMe(): Promise<UserInfo> {
    const response = await apiClient.get<UserInfo>('/api/v1/auth/me/');
    return response.data;
  },

  /**
   * Refresca el access token usando el refresh token
   */
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await axios.post<RefreshTokenResponse>(
      `${API_BASE_URL}/api/v1/auth/refresh/`,
      { refresh: refreshToken }
    );
    return response.data;
  },

  /**
   * Guarda los tokens en localStorage
   */
  saveTokens(tokens: AuthTokens): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  },

  /**
   * Verifica si hay un token guardado
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
