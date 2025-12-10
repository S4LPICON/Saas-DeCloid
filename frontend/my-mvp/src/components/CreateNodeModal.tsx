import { useState } from 'react';
import type { FormEvent } from 'react';
import { apiService } from '../services/api.service';
import './CreateServerModal.css';

interface CreateNodeModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateNodeModal = ({ onClose, onSuccess }: CreateNodeModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    ip_address: '',
    location: '',
    daemon_port: 8080,
    daemon_sftp_port: 2022,
    cpu_cores: 4,
    cpu_over_allocation: 1.5,
    memory: 8192,
    memory_over_allocation: 1.2,
    storage: 50000,
    storage_over_allocation: 1.1,
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiService.createNode(formData);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creando nodo:', err);
      
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
          setError(errorData.message || errorData.detail || 'Error al crear el nodo');
        }
      } else {
        setError('Error al crear el nodo. Por favor, verifica los datos.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Crear Nuevo Nodo</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Nombre del Nodo *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Nodo Principal"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="ip_address">Dirección IP *</label>
              <input
                id="ip_address"
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                placeholder="192.168.1.100"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="location">Ubicación *</label>
              <input
                id="location"
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="US-East"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="daemon_port">Puerto Daemon *</label>
              <input
                id="daemon_port"
                type="number"
                value={formData.daemon_port}
                onChange={(e) => setFormData({ ...formData, daemon_port: parseInt(e.target.value) })}
                min="1"
                max="65535"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="daemon_sftp_port">Puerto SFTP *</label>
              <input
                id="daemon_sftp_port"
                type="number"
                value={formData.daemon_sftp_port}
                onChange={(e) => setFormData({ ...formData, daemon_sftp_port: parseInt(e.target.value) })}
                min="1"
                max="65535"
                required
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-section-title">Recursos del Hardware</div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="cpu_cores">CPU Cores *</label>
              <input
                id="cpu_cores"
                type="number"
                value={formData.cpu_cores}
                onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
                min="1"
                max="128"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="cpu_over_allocation">CPU Over-allocation</label>
              <input
                id="cpu_over_allocation"
                type="number"
                step="0.1"
                value={formData.cpu_over_allocation}
                onChange={(e) => setFormData({ ...formData, cpu_over_allocation: parseFloat(e.target.value) })}
                min="1"
                max="10"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="memory">Memoria (MB) *</label>
              <input
                id="memory"
                type="number"
                value={formData.memory}
                onChange={(e) => setFormData({ ...formData, memory: parseInt(e.target.value) })}
                min="1024"
                max="1048576"
                step="1024"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="memory_over_allocation">Memory Over-allocation</label>
              <input
                id="memory_over_allocation"
                type="number"
                step="0.1"
                value={formData.memory_over_allocation}
                onChange={(e) => setFormData({ ...formData, memory_over_allocation: parseFloat(e.target.value) })}
                min="1"
                max="10"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="storage">Almacenamiento (MB) *</label>
              <input
                id="storage"
                type="number"
                value={formData.storage}
                onChange={(e) => setFormData({ ...formData, storage: parseInt(e.target.value) })}
                min="0"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="storage_over_allocation">Storage Over-allocation</label>
              <input
                id="storage_over_allocation"
                type="number"
                step="0.1"
                value={formData.storage_over_allocation}
                onChange={(e) => setFormData({ ...formData, storage_over_allocation: parseFloat(e.target.value) })}
                min="1"
                max="10"
                disabled={loading}
              />
            </div>
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
              {loading ? 'Creando...' : 'Crear Nodo'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
