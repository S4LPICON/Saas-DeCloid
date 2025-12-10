import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

export const Dashboard = () => {
  const navigate = useNavigate();

  const cards = [
    {
      title: 'Nodos',
      description: 'Gestiona y visualiza todos tus nodos',
      icon: '🔷',
      path: '/nodes',
      color: '#667eea',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
    {
      title: 'Servidores',
      description: 'Administra tus servidores y su estado',
      icon: '🖥️',
      path: '/servers',
      color: '#f093fb',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    },
    {
      title: 'Artefactos',
      description: 'Explora y gestiona tus artefactos',
      icon: '📦',
      path: '/artifacts',
      color: '#4facfe',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    },
  ];

  return (
    <div className="dashboard-container">
      {/* Header con botón de cuenta */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">DeCloid Dashboard</h1>
          <button onClick={() => navigate('/account')} className="account-button">
            <span className="account-icon">👤</span>
            <span>Mi Cuenta</span>
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="dashboard-main">
        <div className="cards-container">
          {cards.map((card) => (
            <div
              key={card.path}
              className="dashboard-card"
              onClick={() => navigate(card.path)}
              style={{ background: card.gradient }}
            >
              <div className="card-icon">{card.icon}</div>
              <h2 className="card-title">{card.title}</h2>
              <p className="card-description">{card.description}</p>
              <div className="card-arrow">→</div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};
