import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Users, 
  Search, 
  Filter, 
  Plus, 
  Download,
  UserCheck,
  Clock,
  AlertCircle,
  Plane
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { crewsApi } from '@/api/crews';
import CrewCard from '@/components/CrewList/CrewCard';
import SearchBar from '@/components/Filters/SearchBar';

const Crew = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [positionFilter, setPositionFilter] = useState<string>('all');

  const { data: crews = [], isLoading } = useQuery({
    queryKey: ['crews'],
    queryFn: crewsApi.getCrews,
  });

  // Filter crews based on search and filters
  const filteredCrews = crews.filter(crew => {
    const matchesSearch = !searchQuery || 
      `${crew.firstName} ${crew.lastName}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
      crew.employeeNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      crew.homeBase.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || crew.status === statusFilter;
    const matchesPosition = positionFilter === 'all' || crew.position === positionFilter;

    return matchesSearch && matchesStatus && matchesPosition;
  });

  // Calculate statistics
  const availableCrew = crews.filter(c => c.status === 'available').length;
  const onLeaveCrew = crews.filter(c => c.status === 'on_leave').length;
  const sickCrew = crews.filter(c => c.status === 'sick_leave').length;
  const expiringLicenses = crews.filter(c => {
    const expiryDate = new Date(c.licenseExpiry);
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
    return expiryDate <= thirtyDaysFromNow;
  }).length;

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'available', label: 'Available' },
    { value: 'on_leave', label: 'On Leave' },
    { value: 'sick_leave', label: 'Sick Leave' },
    { value: 'training', label: 'Training' },
    { value: 'standby', label: 'Standby' },
  ];

  const positionOptions = [
    { value: 'all', label: 'All Positions' },
    { value: 'Captain', label: 'Captain' },
    { value: 'First Officer', label: 'First Officer' },
    { value: 'Flight Attendant', label: 'Flight Attendant' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="glass-card p-8">
          <div className="space-y-4 animate-pulse">
            <div className="h-6 bg-muted rounded w-1/3"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-48 bg-muted rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Crew Management</h1>
          <p className="text-muted-foreground">
            Manage crew members, availability, and qualifications
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" className="glass-button">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button className="glass-button bg-primary hover:bg-primary/90">
            <Plus className="h-4 w-4 mr-2" />
            Add Crew Member
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Available</p>
                <p className="text-2xl font-bold text-success">{availableCrew}</p>
              </div>
              <UserCheck className="h-8 w-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">On Leave</p>
                <p className="text-2xl font-bold text-warning">{onLeaveCrew}</p>
              </div>
              <Clock className="h-8 w-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Sick Leave</p>
                <p className="text-2xl font-bold text-destructive">{sickCrew}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">License Expiring</p>
                <p className="text-2xl font-bold text-accent">{expiringLicenses}</p>
              </div>
              <Plane className="h-8 w-8 text-accent" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card className="glass-card">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <SearchBar
                placeholder="Search by name, employee number, or base..."
                value={searchQuery}
                onChange={setSearchQuery}
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="glass px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <select
                value={positionFilter}
                onChange={(e) => setPositionFilter(e.target.value)}
                className="glass px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {positionOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <Button variant="outline" size="sm" className="glass-button">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/20">
            <p className="text-sm text-muted-foreground">
              Showing {filteredCrews.length} of {crews.length} crew members
            </p>
            
            {(statusFilter !== 'all' || positionFilter !== 'all' || searchQuery) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('all');
                  setPositionFilter('all');
                }}
                className="text-muted-foreground hover:text-foreground"
              >
                Clear Filters
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Crew Grid */}
      {filteredCrews.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCrews.map((crew) => (
            <CrewCard key={crew.id} crew={crew} />
          ))}
        </div>
      ) : (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">No crew members found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || statusFilter !== 'all' || positionFilter !== 'all'
                ? 'Try adjusting your search criteria or filters.'
                : 'No crew members are currently registered in the system.'
              }
            </p>
            {(searchQuery || statusFilter !== 'all' || positionFilter !== 'all') && (
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery('');
                  setStatusFilter('all');
                  setPositionFilter('all');
                }}
                className="glass-button"
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Crew;