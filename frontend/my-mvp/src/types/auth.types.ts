export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface RefreshTokenRequest {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  plan: {
    name: string;
    nodes: number;
    images: number;
    price: number;
  };
  usage: {
    nodes_used: number;
    images_used: number;
  };
}
