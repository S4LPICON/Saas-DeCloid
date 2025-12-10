import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { apiService } from '../services/api.service';
import type { Node, Artifact } from '../types/api.types';
import './CreateServerModal.css';

interface CreateServerModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateServerModal = ({ onClose, onSuccess }: CreateServerModalProps) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    node: '',
    artifact: '',
    max_players: 20,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [nodesData, artifactsData] = await Promise.all([
        apiService.getNodes(),
        apiService.getArtifacts(),
      ]);
      setNodes(nodesData);
      setArtifacts(artifactsData);
    } catch (err) {
      console.error('Error cargando datos:', err);
      setError('Error al cargar nodos y artefactos');
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiService.createServer({
        name: formData.name,
        node: formData.node,
        artifact: formData.artifact,
        max_players: formData.max_players,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creando servidor:', err);
      
      // Mejorar manejo de errores
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Si es un objeto con campos específicos
        if (typeof errorData === 'object' && !errorData.message) {
          const errorMessages = Object.entries(errorData)
            .map(([field, messages]) => {
              if (Array.isArray(messages)) {
                return `${field}: ${messages.join(', ')}`;
              }
              return `${field}: ${messages}`;
            })
            .join('\n');
          setError(errorMessages);
        } else {
          setError(errorData.message || errorData.detail || 'Error al crear el servidor');
        }
      } else {
        setError('Error al crear el servidor. Por favor, verifica los datos.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Crear Nuevo Servidor</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">Nombre del Servidor *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Mi Servidor Minecraft"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="node">Nodo *</label>
            <select
              id="node"
              value={formData.node}
              onChange={(e) => setFormData({ ...formData, node: e.target.value })}
              required
              disabled={loading}
            >
              <option value="">Selecciona un nodo</option>
              {nodes.map((node) => (
                <option key={node.node_uuid} value={node.node_uuid}>
                  {node.name} ({node.ip_address})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="artifact">Artefacto *</label>
            <select
              id="artifact"
              value={formData.artifact}
              onChange={(e) => setFormData({ ...formData, artifact: e.target.value })}
              required
              disabled={loading}
            >
              <option value="">Selecciona un artefacto</option>
              {artifacts.filter(a => a.status === 'ready').map((artifact) => (
                <option key={artifact.artifact_uuid} value={artifact.artifact_uuid}>
                  {artifact.name} (v{artifact.mc_version})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="max_players">Jugadores Máximos</label>
            <input
              id="max_players"
              type="number"
              value={formData.max_players}
              onChange={(e) => setFormData({ ...formData, max_players: parseInt(e.target.value) })}
              min="1"
              max="1000"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="modal-error">
              {error.split('\n').map((line, i) => (
                <div key={i}>{line}</div>
              ))}
            </div>
          )}

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-cancel" disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? 'Creando...' : 'Crear Servidor'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
