import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import AppShell from './components/AppShell';
import { isAuthenticated } from './api/apiClient';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Roster = lazy(() => import('./pages/Roster'));
const Crew = lazy(() => import('./pages/Crew'));
const Disruptions = lazy(() => import('./pages/Disruptions'));
const Settings = lazy(() => import('./pages/Settings'));
const Login = lazy(() => import('./pages/Login'));

// Loading component
const PageSkeleton = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="glass-card p-8 w-full max-w-md">
      <div className="space-y-4 animate-pulse">
        <div className="h-4 bg-muted rounded w-3/4"></div>
        <div className="h-4 bg-muted rounded w-1/2"></div>
        <div className="h-4 bg-muted rounded w-5/6"></div>
      </div>
    </div>
  </div>
);

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

// Public Route wrapper (redirects authenticated users)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <Suspense fallback={<PageSkeleton />}>
              <Login />
            </Suspense>
          </PublicRoute>
        } 
      />

      {/* Protected routes within AppShell */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell>
              <Suspense fallback={<PageSkeleton />}>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/roster" element={<Roster />} />
                  <Route path="/crew" element={<Crew />} />
                  <Route path="/disruptions" element={<Disruptions />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Suspense>
            </AppShell>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

export default AppRoutes;