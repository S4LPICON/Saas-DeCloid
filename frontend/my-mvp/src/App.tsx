import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { authService } from './services/auth.service'
import { LoginPage } from './pages/LoginPage'
import { Dashboard } from './pages/Dashboard'
import { NodesPage } from './pages/NodesPage'
import { ServersPage } from './pages/ServersPage'
import { ArtifactsPage } from './pages/ArtifactsPage'
import { AccountPage } from './pages/AccountPage'
import './App.css'

// Componente para proteger rutas
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/nodes"
          element={
            <ProtectedRoute>
              <NodesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/servers"
          element={
            <ProtectedRoute>
              <ServersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/artifacts"
          element={
            <ProtectedRoute>
              <ArtifactsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
