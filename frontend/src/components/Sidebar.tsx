import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Calendar, 
  Users, 
  AlertTriangle, 
  Settings,
  ChevronLeft,
  Plane,
  BarChart3
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Operations overview and KPIs'
  },
  {
    name: 'Roster',
    href: '/roster',
    icon: Calendar,
    description: 'Crew scheduling and assignments'
  },
  {
    name: 'Crew',
    href: '/crew',
    icon: Users,
    description: 'Crew management and profiles'
  },
  {
    name: 'Disruptions',
    href: '/disruptions',
    icon: AlertTriangle,
    description: 'Active disruptions and alerts'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration'
  }
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();

  return (
    <>
      {/* Desktop Sidebar */}
      <div
        className={cn(
          'fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 glass-card border-r border-glass-border/20 z-30',
          'transform transition-transform duration-300 ease-smooth',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'lg:translate-x-0' // Always visible on large screens
        )}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-border/20">
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-6 h-6 bg-primary/10 rounded">
              <BarChart3 className="h-4 w-4 text-primary" />
            </div>
            <span className="font-medium text-sm text-foreground">Navigation</span>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="lg:hidden glass-button p-1"
            aria-label="Close sidebar"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            
            return (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => window.innerWidth < 1024 && onClose()}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200',
                  'group hover:bg-primary/5 hover:text-primary',
                  isActive 
                    ? 'bg-primary/10 text-primary border border-primary/20 shadow-sm' 
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                <Icon 
                  className={cn(
                    'h-5 w-5 transition-colors duration-200',
                    isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-primary'
                  )} 
                />
                <div className="flex-1 min-w-0">
                  <div className={cn(
                    'font-medium',
                    isActive ? 'text-primary' : 'text-foreground'
                  )}>
                    {item.name}
                  </div>
                  <div className="text-xs text-muted-foreground truncate">
                    {item.description}
                  </div>
                </div>
                
                {isActive && (
                  <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse-glow" />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-border/20">
          <div className="glass rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-2">
              <Plane className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-foreground">System Status</span>
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>Active Flights</span>
                <span className="text-primary font-medium">24</span>
              </div>
              <div className="flex justify-between">
                <span>Available Crew</span>
                <span className="text-success font-medium">156</span>
              </div>
              <div className="flex justify-between">
                <span>Active Alerts</span>
                <span className="text-warning font-medium">3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;