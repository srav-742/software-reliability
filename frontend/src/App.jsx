import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import CreateProject from './pages/CreateProject';
import ProjectDetails from './pages/ProjectDetails';
import Analysis from './pages/Analysis';
import Prediction from './pages/Prediction';
import Explainability from './pages/Explainability';
import Recommendations from './pages/Recommendations';
import Training from './pages/Training';
import CicdIntegration from './pages/CicdIntegration';
import ApiKeyScanner from './pages/ApiKeyScanner';
import Reports from './pages/Reports';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Application Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/create" element={<CreateProject />} />
            <Route path="projects/:id" element={<ProjectDetails />} />
            <Route path="analysis" element={<Analysis />} />
            <Route path="prediction" element={<Prediction />} />
            <Route path="explainability" element={<Explainability />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="training" element={<Training />} />
            <Route path="cicd" element={<CicdIntegration />} />
            <Route path="api-key-scanner" element={<ApiKeyScanner />} />
            <Route path="reports" element={<Reports />} />
            <Route path="profile" element={<Profile />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
