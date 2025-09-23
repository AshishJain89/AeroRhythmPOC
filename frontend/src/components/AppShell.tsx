import Header from './Header';
import { useLocation } from 'react-router-dom';

interface AppShellProps {
  children: React.ReactNode;
}

const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const location = useLocation();

  // Get page title based on route
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard':
        return 'Operations Dashboard';
      case '/roster':
        return 'Crew Roster Management';
      case '/crew':
        return 'Crew Management';
      case '/disruptions':
        return 'Disruptions & Alerts';
      case '/settings':
        return 'System Settings';
      default:
        return 'Crew Rostering System';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header with Navigation */}
      <Header pageTitle={getPageTitle()} />

      {/* Main Content */}
      <main className="pt-6 pb-12 px-6 overflow-auto custom-scrollbar">
        <div className="max-w-7xl mx-auto">
          <div className="glass-card rounded-2xl p-8">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AppShell;