import { useState } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { apiService } from '../services/api.service';
import './CreateServerModal.css';

interface CreateArtifactModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export const CreateArtifactModal = ({ onClose, onSuccess }: CreateArtifactModalProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [zipFile, setZipFile] = useState<File | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'paper',
    java_version: '21',
    mc_version: '1.20.1',
    cpu_cores: 2,
    memory_in_mb: 1024,
  });

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.zip')) {
        setError('El archivo debe ser un ZIP');
        setZipFile(null);
        e.target.value = '';
        return;
      }
      setError('');
      setZipFile(file);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!zipFile) {
      setError('Debes seleccionar un archivo ZIP');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('type', formData.type);
      formDataToSend.append('java_version', formData.java_version);
      formDataToSend.append('mc_version', formData.mc_version);
      formDataToSend.append('cpu_cores', formData.cpu_cores.toString());
      formDataToSend.append('memory_in_mb', formData.memory_in_mb.toString());
      formDataToSend.append('zip_file', zipFile);

      await apiService.createArtifactWithFile(formDataToSend);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Error creando artefacto:', err);
      
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
          setError(errorData.message || errorData.detail || 'Error al crear el artefacto');
        }
      } else {
        setError('Error al crear el artefacto. Por favor, verifica los datos.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Crear Nuevo Artefacto</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">Nombre del Artefacto *</label>
            <input
              id="name"
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Mi Artefacto"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Descripción</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Descripción del artefacto..."
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="zip_file">Archivo ZIP *</label>
            <input
              id="zip_file"
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              required
              disabled={loading}
            />
            {zipFile && (
              <p className="file-info">📦 {zipFile.name} ({(zipFile.size / 1024 / 1024).toFixed(2)} MB)</p>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="type">Tipo *</label>
            <select
              id="type"
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              required
              disabled={loading}
            >
              <option value="paper">Paper</option>
              <option value="spigot">Spigot</option>
              <option value="vanilla">Vanilla</option>
              <option value="forge">Forge</option>
              <option value="fabric">Fabric</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="mc_version">Versión de Minecraft *</label>
            <input
              id="mc_version"
              type="text"
              value={formData.mc_version}
              onChange={(e) => setFormData({ ...formData, mc_version: e.target.value })}
              placeholder="1.20.1"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="java_version">Versión de Java *</label>
            <select
              id="java_version"
              value={formData.java_version}
              onChange={(e) => setFormData({ ...formData, java_version: e.target.value })}
              required
              disabled={loading}
            >
              <option value="8">Java 8</option>
              <option value="11">Java 11</option>
              <option value="17">Java 17</option>
              <option value="21">Java 21</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="cpu_cores">CPU Cores *</label>
            <input
              id="cpu_cores"
              type="number"
              value={formData.cpu_cores}
              onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
              min="1"
              max="32"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="memory_in_mb">Memoria (MB) *</label>
            <input
              id="memory_in_mb"
              type="number"
              value={formData.memory_in_mb}
              onChange={(e) => setFormData({ ...formData, memory_in_mb: parseInt(e.target.value) })}
              min="512"
              max="32768"
              step="512"
              required
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
              {loading ? 'Creando...' : 'Crear Artefacto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
