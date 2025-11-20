import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';
import { ToastProvider } from './components/Toast';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProjectWizard from './pages/ProjectWizard';
import ProjectDetail from './pages/ProjectDetail';
import AdminPanel from './pages/AdminPanel';
import MunicipalPortal from './pages/MunicipalPortal';
import RulesBrowser from './pages/RulesBrowser';
import AIAssistant from './pages/AIAssistant';

const queryClient = new QueryClient();

function PrivateRoute({ children }) {
  const { token } = useAuthStore();
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={
            <PrivateRoute><Dashboard /></PrivateRoute>
          } />
          <Route path="/project/new" element={
            <PrivateRoute><ProjectWizard /></PrivateRoute>
          } />
          <Route path="/project/:id" element={
            <PrivateRoute><ProjectDetail /></PrivateRoute>
          } />
          <Route path="/admin" element={
            <PrivateRoute><AdminPanel /></PrivateRoute>
          } />
          <Route path="/municipal" element={
            <PrivateRoute><MunicipalPortal /></PrivateRoute>
          } />
          <Route path="/rules" element={
            <PrivateRoute><RulesBrowser /></PrivateRoute>
          } />
          <Route path="/ai-assistant" element={
            <PrivateRoute><AIAssistant /></PrivateRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

export default App;
