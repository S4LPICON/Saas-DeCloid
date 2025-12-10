import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api.service';
import { CreateArtifactModal } from '../components/CreateArtifactModal';
import type { Artifact } from '../types/api.types';
import './ResourcePage.css';

export const ArtifactsPage = () => {
  const navigate = useNavigate();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [buildingArtifact, setBuildingArtifact] = useState<string | null>(null);
  const [deletingArtifact, setDeletingArtifact] = useState<string | null>(null);

  useEffect(() => {
    loadArtifacts();
  }, []);

  const loadArtifacts = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiService.getArtifacts();
      setArtifacts(data);
    } catch (err: any) {
      console.error('Error cargando artefactos:', err);
      setError('Error al cargar los artefactos');
    } finally {
      setLoading(false);
    }
  };

  const handleBuild = async (artifactUuid: string, artifactName: string) => {
    if (!confirm(`¿Iniciar el build del artefacto "${artifactName}"?`)) {
      return;
    }

    try {
      setBuildingArtifact(artifactUuid);
      await apiService.buildArtifact(artifactUuid);
      alert('Build iniciado correctamente');
      await loadArtifacts();
    } catch (err: any) {
      console.error('Error en build:', err);
      const errorDetail = err.response?.data?.detail;
      
      if (errorDetail === 'A build is already in progress') {
        alert('Ya hay un build en progreso para este artefacto. Por favor espera a que termine.');
      } else {
        alert(err.response?.data?.message || err.response?.data?.detail || 'Error al iniciar el build');
      }
    } finally {
      setBuildingArtifact(null);
    }
  };

  const handleDelete = async (artifactUuid: string, artifactName: string) => {
    if (!confirm(`¿Estás seguro de eliminar el artefacto "${artifactName}"?`)) {
      return;
    }

    try {
      setDeletingArtifact(artifactUuid);
      await apiService.deleteArtifact(artifactUuid);
      await loadArtifacts();
    } catch (err: any) {
      console.error('Error eliminando artefacto:', err);
      alert('Error al eliminar el artefacto');
    } finally {
      setDeletingArtifact(null);
    }
  };

  const formatSize = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(2)} GB`;
    }
    return `${mb} MB`;
  };

  const canBuild = (artifact: Artifact) => {
    // Permitir build si el artefacto ha sido actualizado después de crearlo
    // o si nunca se ha hecho build exitosamente (status !== 'success')
    const hasChanges = new Date(artifact.update_date).getTime() > new Date(artifact.creation_date).getTime();
    const neverBuilt = artifact.status !== 'success';
    return hasChanges || neverBuilt;
  };

  const getBuildButtonText = (artifact: Artifact, isBuilding: boolean) => {
    if (isBuilding) return '⚙️ Construyendo...';
    if (!canBuild(artifact)) return '✓ Build actualizado';
    return '⚙️ Build';
  };

  return (
    <div className="resource-page">
      <header className="resource-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Volver
        </button>
        <h1 className="resource-title">
          <span className="resource-icon">📦</span>
          Artefactos
        </h1>
        <button onClick={() => setShowCreateModal(true)} className="create-button">
          + Crear Artefacto
        </button>
      </header>

      <main className="resource-main">
        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Cargando artefactos...</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <p className="error-text">{error}</p>
            <button onClick={loadArtifacts} className="retry-button">
              Reintentar
            </button>
          </div>
        )}

        {!loading && !error && artifacts.length === 0 && (
          <div className="empty-container">
            <p className="empty-text">No hay artefactos disponibles</p>
            <button onClick={() => setShowCreateModal(true)} className="create-button-large">
              + Crear Primer Artefacto
            </button>
          </div>
        )}

        {!loading && !error && artifacts.length > 0 && (
          <div className="resource-grid">
            {artifacts.map((artifact) => (
              <div key={artifact.artifact_uuid} className="resource-card">
                <div className="resource-card-header">
                  <h3 className="resource-card-title">{artifact.name}</h3>
                  <span className={`status-badge status-${artifact.status.toLowerCase()}`}>
                    {artifact.status}
                  </span>
                </div>
                <div className="resource-card-body">
                  <p><strong>Tipo:</strong> {artifact.type}</p>
                  <p><strong>Java:</strong> {artifact.java_version}</p>
                  <p><strong>MC Version:</strong> {artifact.mc_version}</p>
                  <p><strong>Tamaño:</strong> {formatSize(artifact.size_in_mb)}</p>
                  <p><strong>CPU:</strong> {artifact.cpu_cores} cores</p>
                  <p><strong>Memoria:</strong> {artifact.memory_in_mb} MB</p>
                  <p><strong>Instancias:</strong> {artifact.active_instances}</p>
                  <p><strong>Creado:</strong> {new Date(artifact.creation_date).toLocaleDateString()}</p>
                  {artifact.update_date && new Date(artifact.update_date).getTime() > new Date(artifact.creation_date).getTime() && (
                    <p><strong>Actualizado:</strong> {new Date(artifact.update_date).toLocaleDateString()}</p>
                  )}
                </div>
                {artifact.description && (
                  <div className="artifact-description">
                    <p>{artifact.description}</p>
                  </div>
                )}
                <div className="resource-card-actions">
                  <button
                    onClick={() => handleBuild(artifact.artifact_uuid, artifact.name)}
                    className="build-button"
                    disabled={
                      buildingArtifact === artifact.artifact_uuid || 
                      artifact.status === 'building' ||
                      !canBuild(artifact)
                    }
                    title={!canBuild(artifact) ? 'No hay cambios desde el último build' : ''}
                  >
                    {getBuildButtonText(artifact, buildingArtifact === artifact.artifact_uuid)}
                  </button>
                  <button
                    onClick={() => handleDelete(artifact.artifact_uuid, artifact.name)}
                    className="delete-button"
                    disabled={deletingArtifact === artifact.artifact_uuid}
                  >
                    {deletingArtifact === artifact.artifact_uuid ? '🗑️ Eliminando...' : '🗑️ Eliminar'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showCreateModal && (
        <CreateArtifactModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={loadArtifacts}
        />
      )}
    </div>
  );
};
