import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import MainLayout from './components/MainLayout';

import Dashboard from './pages/Dashboard';
import RoomPage from './pages/RoomPage';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import CreateRoomPage from './pages/CreateRoomPage';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

import ProtectedRoute from './features/auth/ProtectedRoute';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>

        {/* AUTH */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* APP WRAPPED LAYOUT */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Dashboard />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/room/:roomId"
          element={
            <ProtectedRoute>
              <MainLayout>
                <RoomPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/create-room"
          element={
            <ProtectedRoute>
              <MainLayout>
                <CreateRoomPage />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Profile />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <MainLayout>
                <Settings />
              </MainLayout>
            </ProtectedRoute>
          }
        />

      </Routes>
    </Router>
  );
};

export default App;