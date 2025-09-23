import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Plane,
  ChevronDown,
  Home, 
  Calendar, 
  Users, 
  AlertTriangle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { authApi } from '@/api/auth';
import { removeAuthToken } from '@/api/apiClient';
import { useNavigate, NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

interface HeaderProps {
  pageTitle: string;
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    name: 'Roster',
    href: '/roster',
    icon: Calendar,
  },
  {
    name: 'Crew',
    href: '/crew',
    icon: Users,
  },
  {
    name: 'Disruptions',
    href: '/disruptions',
    icon: AlertTriangle,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  }
];

const Header: React.FC<HeaderProps> = ({ pageTitle }) => {
  const [notificationCount] = useState(3);
  const navigate = useNavigate();
  const location = useLocation();

  const { data: user } = useQuery({
    queryKey: ['current-user'],
    queryFn: authApi.getCurrentUser,
  });

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } finally {
      removeAuthToken();
      navigate('/login');
    }
  };

  return (
    <div className="sticky top-0 z-50">
      {/* Main Header */}
      <header className="h-16 glass-card border-b border-glass-border/20 backdrop-blur-glass">
        <div className="flex items-center justify-between h-full px-6">
          {/* Left Section - Logo & Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-primary to-primary-glow rounded-xl shadow-lg">
                <Plane className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-primary-glow bg-clip-text text-transparent">
                  IndiGo Crew
                </h1>
                <p className="text-sm text-muted-foreground -mt-1">Operations Control</p>
              </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-3">
            {/* System Status Indicator */}
            <div className="hidden md:flex items-center space-x-2 text-sm glass px-3 py-1.5 rounded-full">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse-glow"></div>
              <span className="text-muted-foreground">All Systems Operational</span>
            </div>

            {/* Notifications */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="glass-button relative rounded-full w-10 h-10"
                aria-label="Notifications"
              >
                <Bell className="h-5 w-5" />
                {notificationCount > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs animate-pulse-glow"
                  >
                    {notificationCount}
                  </Badge>
                )}
              </Button>
            </div>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="glass-button flex items-center space-x-2 px-4 py-2 rounded-full"
                >
                  <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary/20 to-primary-glow/20 rounded-full">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div className="hidden md:block text-left">
                    <p className="text-sm font-medium text-foreground">
                      {user?.username || 'Loading...'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {user?.role?.replace('_', ' ') || 'User'}
                    </p>
                  </div>
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-56 glass-card backdrop-blur-glass">
                <div className="px-3 py-2 border-b border-border/20">
                  <p className="text-sm font-medium">{user?.username}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
                
                <DropdownMenuItem className="cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                
                <DropdownMenuItem 
                  className="cursor-pointer"
                  onClick={() => navigate('/settings')}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                
                <DropdownMenuSeparator />
                
                <DropdownMenuItem 
                  className="cursor-pointer text-destructive focus:text-destructive"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="glass-card border-b border-glass-border/20 backdrop-blur-glass">
        <div className="px-6">
          <div className="flex space-x-1 overflow-x-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;
              
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 relative',
                    'hover:bg-primary/5 hover:text-primary whitespace-nowrap',
                    isActive 
                      ? 'text-primary bg-gradient-to-r from-primary/10 to-primary-glow/10 shadow-sm' 
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                >
                  <Icon 
                    className={cn(
                      'h-4 w-4 transition-colors duration-200',
                      isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-primary'
                    )} 
                  />
                  <span>{item.name}</span>
                  
                  {isActive && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary to-primary-glow rounded-full" />
                  )}
                </NavLink>
              );
            })}
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Header;