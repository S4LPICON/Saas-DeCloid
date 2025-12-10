import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api.service';
import type { Server } from '../types/api.types';
import './ResourcePage.css';

export const ServersPage = () => {
  const navigate = useNavigate();
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingServer, setDeletingServer] = useState<string | null>(null);

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.getServers();
      setServers(data);
    } catch (err: any) {
      console.error('Error cargando servidores:', err);
      setError('Error al cargar los servidores');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (serverUuid: string, serverName: string) => {
    if (!confirm(`¿Estás seguro de eliminar el servidor "${serverName}"?`)) {
      return;
    }

    try {
      setDeletingServer(serverUuid);
      await apiService.deleteServer(serverUuid);
      await loadServers();
    } catch (err: any) {
      console.error('Error eliminando servidor:', err);
      alert('Error al eliminar el servidor');
    } finally {
      setDeletingServer(null);
    }
  };

  return (
    <div className="resource-page">
      <header className="resource-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Volver
        </button>
        <h1 className="resource-title">
          <span className="resource-icon">🖥️</span>
          Servidores
        </h1>
      </header>

      <main className="resource-main">
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Cargando servidores...</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <p className="error-text">{error}</p>
            <button onClick={loadServers} className="retry-button">
              Reintentar
            </button>
          </div>
        )}

        {!loading && !error && servers.length === 0 && (
          <div className="empty-container">
            <p className="empty-text">No hay servidores disponibles</p>
          </div>
        )}

        {!loading && !error && servers.length > 0 && (
          <div className="resource-grid">
            {servers.map((server) => (
              <div key={server.server_uuid} className="resource-card">
                <div className="resource-card-header">
                  <h3 className="resource-card-title">{server.name}</h3>
                  <span className={`status-badge status-${server.status.toLowerCase()}`}>
                    {server.status}
                  </span>
                </div>
                <div className="resource-card-body">
                  <p><strong>IP:</strong> {server.ip_address}:{server.port}</p>
                  {server.players_online !== undefined && (
                    <p><strong>Jugadores:</strong> {server.players_online}/{server.max_players}</p>
                  )}
                  {server.cpu_allocated && (
                    <p><strong>CPU:</strong> {server.cpu_allocated} cores</p>
                  )}
                  {server.memory_allocated && (
                    <p><strong>Memoria:</strong> {server.memory_allocated} MB</p>
                  )}
                  {server.uptime !== undefined && (
                    <p><strong>Uptime:</strong> {server.uptime} segundos</p>
                  )}
                  {server.create_date && (
                    <p><strong>Creado:</strong> {new Date(server.create_date).toLocaleDateString()}</p>
                  )}
                </div>
                <div className="resource-card-actions">
                  <button
                    onClick={() => handleDelete(server.server_uuid, server.name)}
                    className="delete-button"
                    disabled={deletingServer === server.server_uuid}
                  >
                    {deletingServer === server.server_uuid ? '🗑️ Eliminando...' : '🗑️ Eliminar'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};
