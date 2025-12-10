import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth.service';
import type { UserInfo } from '../types/auth.types';
import './AccountPage.css';

export const AccountPage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await authService.getMe();
      setUser(data);
    } catch (err: any) {
      console.error('Error cargando información del usuario:', err);
      setError('Error al cargar la información');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  const getProgressPercentage = (used: number, total: number) => {
    return total > 0 ? (used / total) * 100 : 0;
  };

  if (loading) {
    return (
      <div className="account-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Cargando información...</p>
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="account-page">
        <div className="error-container">
          <p className="error-text">{error || 'No se pudo cargar la información'}</p>
          <button onClick={() => navigate('/')} className="back-button">
            Volver al Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="account-page">
      <header className="account-header">
        <button onClick={() => navigate('/')} className="back-button">
          ← Volver al Dashboard
        </button>
        <h1 className="account-title">Mi Cuenta</h1>
      </header>

      <main className="account-main">
        {/* Información del Usuario */}
        <div className="account-section">
          <div className="section-header">
            <span className="section-icon">👤</span>
            <h2>Información Personal</h2>
          </div>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Usuario</span>
              <span className="info-value">{user.username}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email</span>
              <span className="info-value">{user.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">ID</span>
              <span className="info-value">#{user.id}</span>
            </div>
          </div>
        </div>

        {/* Plan */}
        <div className="account-section">
          <div className="section-header">
            <span className="section-icon">💎</span>
            <h2>Plan Actual</h2>
          </div>
          <div className="plan-card">
            <div className="plan-header">
              <h3 className="plan-name">{user.plan.name}</h3>
              <span className="plan-price">
                {user.plan.price === 0 ? 'Gratis' : `$${user.plan.price}/mes`}
              </span>
            </div>
            <div className="plan-details">
              <div className="plan-feature">
                <span>✓ {user.plan.nodes} Nodos</span>
              </div>
              <div className="plan-feature">
                <span>✓ {user.plan.images} Imágenes</span>
              </div>
            </div>
          </div>
        </div>

        {/* Uso de Recursos */}
        <div className="account-section">
          <div className="section-header">
            <span className="section-icon">📊</span>
            <h2>Uso de Recursos</h2>
          </div>
          <div className="usage-grid">
            <div className="usage-card">
              <h3>Nodos</h3>
              <div className="usage-stats">
                <span className="usage-numbers">
                  {user.usage.nodes_used} / {user.plan.nodes}
                </span>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${getProgressPercentage(user.usage.nodes_used, user.plan.nodes)}%`,
                    }}
                  ></div>
                </div>
                <span className="usage-percentage">
                  {getProgressPercentage(user.usage.nodes_used, user.plan.nodes).toFixed(0)}% usado
                </span>
              </div>
            </div>

            <div className="usage-card">
              <h3>Imágenes</h3>
              <div className="usage-stats">
                <span className="usage-numbers">
                  {user.usage.images_used} / {user.plan.images}
                </span>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${getProgressPercentage(user.usage.images_used, user.plan.images)}%`,
                    }}
                  ></div>
                </div>
                <span className="usage-percentage">
                  {getProgressPercentage(user.usage.images_used, user.plan.images).toFixed(0)}% usado
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="account-section">
          <div className="actions-grid">
            <button onClick={handleLogout} className="logout-button">
              <span>🚪</span>
              Cerrar Sesión
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
