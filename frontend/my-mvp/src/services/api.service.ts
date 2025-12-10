import { apiClient } from '../config/api.config';
import type { Node, Server, Artifact } from '../types/api.types';

export const apiService = {
  /**
   * Obtiene la lista de nodos
   */
  async getNodes(): Promise<Node[]> {
    const response = await apiClient.get<Node[]>('/api/v1/nodes/');
    return response.data;
  },

  /**
   * Crea un nuevo nodo
   */
  async createNode(nodeData: Partial<Node>): Promise<Node> {
    const response = await apiClient.post<Node>('/api/v1/nodes/', nodeData);
    return response.data;
  },

  /**
   * Actualiza un nodo existente
   */
  async updateNode(nodeUuid: string, nodeData: Partial<Node>): Promise<Node> {
    const response = await apiClient.put<Node>(`/api/v1/nodes/${nodeUuid}/`, nodeData);
    return response.data;
  },

  /**
   * Elimina un nodo
   */
  async deleteNode(nodeUuid: string): Promise<void> {
    await apiClient.delete(`/api/v1/nodes/${nodeUuid}/`);
  },

  /**
   * Obtiene la lista de servidores
   */
  async getServers(): Promise<Server[]> {
    const response = await apiClient.get<Server[]>('/api/v1/servers/');
    return response.data;
  },

  /**
   * Crea un nuevo servidor
   */
  async createServer(serverData: Partial<Server>): Promise<Server> {
    const response = await apiClient.post<Server>('/api/v1/servers/', serverData);
    return response.data;
  },

  /**
   * Elimina un servidor
   */
  async deleteServer(serverUuid: string): Promise<void> {
    await apiClient.delete(`/api/v1/servers/${serverUuid}/`);
  },

  /**
   * Obtiene la lista de artefactos
   */
  async getArtifacts(): Promise<Artifact[]> {
    const response = await apiClient.get<Artifact[]>('/api/v1/artifacts/');
    return response.data;
  },

  /**
   * Crea un nuevo artefacto
   */
  async createArtifact(artifactData: Partial<Artifact>): Promise<Artifact> {
    const response = await apiClient.post<Artifact>('/api/v1/artifacts/', artifactData);
    return response.data;
  },

  /**
   * Crea un nuevo artefacto con archivo ZIP
   */
  async createArtifactWithFile(formData: FormData): Promise<Artifact> {
    const response = await apiClient.post<Artifact>('/api/v1/artifacts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Elimina un artefacto
   */
  async deleteArtifact(artifactUuid: string): Promise<void> {
    await apiClient.delete(`/api/v1/artifacts/${artifactUuid}/`);
  },

  /**
   * Ejecuta el build de un artefacto
   */
  async buildArtifact(artifactUuid: string): Promise<any> {
    const response = await apiClient.post(`/api/v1/artifacts/${artifactUuid}/build/`);
    return response.data;
  },
};
