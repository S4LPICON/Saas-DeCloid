import { useState } from 'react';
import type { Node } from '../types/api.types';
import './NodeSettingsModal.css';

interface NodeSettingsModalProps {
  node: Node;
  onClose: () => void;
  onUpdate: (updatedNode: Partial<Node>) => Promise<void>;
}

export const NodeSettingsModal = ({ node, onClose, onUpdate }: NodeSettingsModalProps) => {
  const [activeTab, setActiveTab] = useState<'basic' | 'config'>('basic');
  const [formData, setFormData] = useState({
    name: node.name,
    ip_address: node.ip_address,
    location: node.location,
    cpu_cores: node.cpu_cores,
    memory: node.memory,
    storage: node.storage,
    daemon_port: node.daemon_port,
    daemon_sftp_port: node.daemon_sftp_port,
  });
  const [saving, setSaving] = useState(false);

  const generateNodeConfig = () => {
    return `debug: false

node:
  uuid: "${node.node_uuid}"
  key: "${node.key}"

docker:
  base_port: ${node.daemon_port}
  max_port: ${node.daemon_port + 35}

api:
  host: 0.0.0.0
  port: ${node.daemon_port}
  ssl:
    enabled: false

default: 25570

remote: "http://localhost:8000"`;
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generateNodeConfig());
    alert('Configuración copiada al portapapeles');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await onUpdate(formData);
      onClose();
    } catch (error) {
      console.error('Error actualizando nodo:', error);
      alert('Error al actualizar el nodo');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content node-settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>⚙️ Configuración del Nodo</h2>
          <button onClick={onClose} className="modal-close">✕</button>
        </div>

        <div className="tabs-container">
          <div className="tabs-header">
            <button
              className={`tab-button ${activeTab === 'basic' ? 'active' : ''}`}
              onClick={() => setActiveTab('basic')}
            >
              📝 Información Básica
            </button>
            <button
              className={`tab-button ${activeTab === 'config' ? 'active' : ''}`}
              onClick={() => setActiveTab('config')}
            >
              🔧 Configuración
            </button>
          </div>

          <div className="tabs-content">
            {activeTab === 'basic' ? (
              <form onSubmit={handleSubmit} className="settings-form">
                <div className="form-section">
                  <h3>Información General</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label htmlFor="name">Nombre *</label>
                      <input
                        type="text"
                        id="name"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="ip_address">Dirección IP *</label>
                      <input
                        type="text"
                        id="ip_address"
                        value={formData.ip_address}
                        onChange={(e) => handleChange('ip_address', e.target.value)}
                        placeholder="192.168.1.100"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="location">Ubicación *</label>
                      <input
                        type="text"
                        id="location"
                        value={formData.location}
                        onChange={(e) => handleChange('location', e.target.value)}
                        placeholder="Ciudad, País"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Hardware</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label htmlFor="cpu_cores">CPU Cores *</label>
                      <input
                        type="number"
                        id="cpu_cores"
                        value={formData.cpu_cores}
                        onChange={(e) => handleChange('cpu_cores', parseInt(e.target.value))}
                        min="1"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="memory">Memoria (MB) *</label>
                      <input
                        type="number"
                        id="memory"
                        value={formData.memory}
                        onChange={(e) => handleChange('memory', parseInt(e.target.value))}
                        min="1"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="storage">Almacenamiento (MB) *</label>
                      <input
                        type="number"
                        id="storage"
                        value={formData.storage}
                        onChange={(e) => handleChange('storage', parseInt(e.target.value))}
                        min="1"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Puertos</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label htmlFor="daemon_port">Puerto Daemon *</label>
                      <input
                        type="number"
                        id="daemon_port"
                        value={formData.daemon_port}
                        onChange={(e) => handleChange('daemon_port', parseInt(e.target.value))}
                        min="1"
                        max="65535"
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label htmlFor="daemon_sftp_port">Puerto SFTP *</label>
                      <input
                        type="number"
                        id="daemon_sftp_port"
                        value={formData.daemon_sftp_port}
                        onChange={(e) => handleChange('daemon_sftp_port', parseInt(e.target.value))}
                        min="1"
                        max="65535"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="form-actions">
                  <button type="button" onClick={onClose} className="cancel-button">
                    Cancelar
                  </button>
                  <button type="submit" className="submit-button" disabled={saving}>
                    {saving ? '💾 Guardando...' : '💾 Guardar Cambios'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="config-tab">
                <div className="config-info">
                  <p>Esta es la configuración que debes usar en el daemon del nodo.</p>
                </div>
                <div className="config-actions">
                  <button onClick={copyToClipboard} className="copy-config-button">
                    📋 Copiar Configuración
                  </button>
                </div>
                <pre className="config-display">
                  {generateNodeConfig()}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
