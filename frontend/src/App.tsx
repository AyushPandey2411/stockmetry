// src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/Login'
import DashboardPage from './pages/Dashboard'
import ForecastingPage from './pages/Forecasting'
import OptimizationPage from './pages/Optimization'
import AnomaliesPage from './pages/Anomalies'
import ProductsPage from './pages/Products'
import UploadPage from './pages/Upload'
import AIAssistantPage from './pages/AIAssistant'
import AboutPage from './pages/About'
import ExecutiveSummary from "./pages/ExecutiveSummary";




function RequireAuth({ children }: { children: JSX.Element }) {
  const token = useAuthStore(s => s.accessToken)
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  const token = useAuthStore(s => s.accessToken)
  return (
    <Routes>
      <Route path="/login" element={token ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route path="/" element={<RequireAuth><AppLayout /></RequireAuth>}>
        <Route index                  element={<DashboardPage />} />
        <Route path="forecasting"     element={<ForecastingPage />} />
        <Route path="optimization"    element={<OptimizationPage />} />
        <Route path="anomalies"       element={<AnomaliesPage />} />
        <Route path="products"        element={<ProductsPage />} />
        <Route path="upload"          element={<UploadPage />} />
        <Route path="ai"              element={<AIAssistantPage />} />
        <Route path="about"           element={<AboutPage />} />
        <Route path="/summary" element={<ExecutiveSummary />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
