import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api.service';
import { CreateNodeModal } from '../components/CreateNodeModal';
import { NodeSettingsModal } from '../components/NodeSettingsModal';
import type { Node } from '../types/api.types';
import './ResourcePage.css';

export const NodesPage = () => {
  const navigate = useNavigate();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [deletingNode, setDeletingNode] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    loadNodes(true);
    
    // Actualizar cada 10 segundos
    const interval = setInterval(() => {
      loadNodes(false); // false = sin mostrar loading
    }, 10000);

    // Limpiar intervalo al desmontar
    return () => clearInterval(interval);
  }, []);

  const loadNodes = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      setError('');
      const data = await apiService.getNodes();
      setNodes(data);
    } catch (err: any) {
      console.error('Error cargando nodos:', err);
      setError('Error al cargar los nodos');
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const handleDelete = async (nodeUuid: string, nodeName: string) => {
    if (!confirm(`¿Estás seguro de eliminar el nodo "${nodeName}"?`)) {
      return;
    }

    try {
      setDeletingNode(nodeUuid);
      await apiService.deleteNode(nodeUuid);
      await loadNodes();
    } catch (err: any) {
      console.error('Error eliminando nodo:', err);
      alert('Error al eliminar el nodo');
    } finally {
      setDeletingNode(null);
    }
  };

  const handleUpdateNode = async (updatedData: Partial<Node>) => {
    if (!selectedNode) return;
    
    try {
      await apiService.updateNode(selectedNode.node_uuid, updatedData);
      await loadNodes();
      setSelectedNode(null);
    } catch (err: any) {
      console.error('Error actualizando nodo:', err);
      throw err;
    }
  };

  return (
    <div className="resource-page">
      <header className="resource-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Volver
        </button>
        <h1 className="resource-title">
          <span className="resource-icon">🔷</span>
          Nodos
        </h1>
        <button onClick={() => setShowCreateModal(true)} className="create-button">
          + Crear Nodo
        </button>
      </header>

      <main className="resource-main">
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Cargando nodos...</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <p className="error-text">{error}</p>
            <button onClick={() => loadNodes(true)} className="retry-button">
              Reintentar
            </button>
          </div>
        )}

        {!loading && !error && nodes.length === 0 && (
          <div className="empty-container">
            <p className="empty-text">No hay nodos disponibles</p>
            <button onClick={() => setShowCreateModal(true)} className="create-button-large">
              + Crear Primer Nodo
            </button>
          </div>
        )}

        {!loading && !error && nodes.length > 0 && (
          <div className="resource-grid">
            {nodes.map((node) => (
              <div key={node.node_uuid} className="resource-card">
                <div className="resource-card-header">
                  <h3 className="resource-card-title">{node.name}</h3>
                  <div className="status-badges">
                    <span className={`status-badge status-${node.status.toLowerCase()}`}>
                      {node.status}
                    </span>
                    <span className={`status-badge ${node.is_online ? 'status-online' : 'status-offline'}`}>
                      {node.is_online ? '🟢 Online' : '🔴 Offline'}
                    </span>
                  </div>
                </div>
                <div className="resource-card-body">
                  <p><strong>IP:</strong> {node.ip_address}</p>
                  <p><strong>Ubicación:</strong> {node.location}</p>
                  <p><strong>CPU:</strong> {node.cpu_cores} cores ({node.cpu_usage.toFixed(1)}% uso)</p>
                  <p><strong>Memoria:</strong> {node.memory} MB ({node.memory_usage.toFixed(1)}% uso)</p>
                  <p><strong>Almacenamiento:</strong> {node.storage} MB ({node.storage_usage.toFixed(1)}% uso)</p>
                  {node.daemon_version && (
                    <p><strong>Daemon:</strong> v{node.daemon_version}</p>
                  )}
                  {node.docker_version && (
                    <p><strong>Docker:</strong> v{node.docker_version}</p>
                  )}
                  {node.servers && node.servers.length > 0 && (
                    <p><strong>Servidores:</strong> {node.servers.length}</p>
                  )}
                  {node.last_heartbeat && (
                    <p><strong>Último heartbeat:</strong> {new Date(node.last_heartbeat).toLocaleString()}</p>
                  )}
                  <p><strong>Creado:</strong> {new Date(node.created_at).toLocaleDateString()}</p>
                </div>
                
                <div className="resource-card-actions">
                  <button
                    onClick={() => setSelectedNode(node)}
                    className="config-button"
                  >
                    ⚙️ Configurar
                  </button>
                  <button
                    onClick={() => handleDelete(node.node_uuid, node.name)}
                    className="delete-button"
                    disabled={deletingNode === node.node_uuid}
                  >
                    {deletingNode === node.node_uuid ? '🗑️ Eliminando...' : '🗑️ Eliminar'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showCreateModal && (
        <CreateNodeModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={loadNodes}
        />
      )}

      {selectedNode && (
        <NodeSettingsModal
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onUpdate={handleUpdateNode}
        />
      )}
    </div>
  );
};
