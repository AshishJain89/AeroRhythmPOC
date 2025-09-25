import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns/format';
import { startOfWeek } from 'date-fns/startOfWeek';
import { endOfWeek } from 'date-fns/endOfWeek';
import { addDays } from 'date-fns/addDays';
import { 
  Calendar, 
  ChevronLeft, 
  ChevronRight, 
  Plus, 
  Filter,
  Download,
  RefreshCw,
  Users,
  Plane
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
// import { rostersApi } from '@/api/rosters';
// import { crewsApi } from '@/api/crews';
import { api } from '@/api/apiClient';
import RosterCalendar from '@/components/RosterCalendar/TimelineView';

const Roster = () => {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [viewMode, setViewMode] = useState<'week' | 'day'>('week');

  const weekStart = startOfWeek(currentWeek);
  const weekEnd = endOfWeek(currentWeek);

  const { data: rostersData, isLoading: rostersLoading } = useQuery({
    queryKey: ['rosters', format(weekStart, 'yyyy-MM-dd'), format(weekEnd, 'yyyy-MM-dd')],
    queryFn: () => api.getRosters(
      format(weekStart, 'yyyy-MM-dd'),
      format(weekEnd, 'yyyy-MM-dd')
    ),
  });

  const { data: crews = [], isLoading: crewsLoading } = useQuery({
    queryKey: ['crews'],
    queryFn: api.getCrews,
  });

  const { data: flights = [], isLoading: flightsLoading } = useQuery({
    queryKey: ['flights'],
    queryFn: api.getFlights,
  });

  const rosters = rostersData?.rosters || [];

  const navigateWeek = (direction: 'prev' | 'next') => {
    setCurrentWeek(prev => addDays(prev, direction === 'next' ? 7 : -7));
  };

  const goToToday = () => {
    setCurrentWeek(new Date());
  };

  // Calculate statistics
  const totalAssignments = rosters.length;
  const confirmedAssignments = rosters.filter(r => r.status === 'confirmed').length;
  const violations = rosters.reduce((acc, r) => acc + r.violations.length, 0);
  const avgConfidence = rosters.length > 0 
    ? rosters.reduce((acc, r) => acc + r.confidence, 0) / rosters.length 
    : 0;

  if (rostersLoading || crewsLoading || flightsLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="glass-card p-8">
          <div className="space-y-4 animate-pulse">
            <div className="h-6 bg-muted rounded w-1/3"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="h-32 bg-muted rounded"></div>
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
          <h1 className="text-2xl font-bold text-foreground">Crew Roster Management</h1>
          <p className="text-muted-foreground">
            Week of {format(weekStart, 'MMM dd')} - {format(weekEnd, 'MMM dd, yyyy')}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" className="glass-button">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" size="sm" className="glass-button">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm" className="glass-button">
            <RefreshCw className="h-4 w-4 mr-2" />
            Optimize
          </Button>
          <Button className="glass-button bg-primary hover:bg-primary/90">
            <Plus className="h-4 w-4 mr-2" />
            New Assignment
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Assignments</p>
                <p className="text-2xl font-bold text-foreground">{totalAssignments}</p>
              </div>
              <Calendar className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Confirmed</p>
                <p className="text-2xl font-bold text-success">{confirmedAssignments}</p>
              </div>
              <Users className="h-8 w-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Violations</p>
                <p className="text-2xl font-bold text-destructive">{violations}</p>
              </div>
              <Badge variant={violations > 0 ? "destructive" : "secondary"}>
                {violations > 0 ? 'Issues' : 'Clean'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Confidence</p>
                <p className="text-2xl font-bold text-accent">{Math.round(avgConfidence * 100)}%</p>
              </div>
              <Plane className="h-8 w-8 text-accent" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Week Navigation */}
      <Card className="glass-card">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Roster Timeline</CardTitle>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 bg-muted/50 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('week')}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    viewMode === 'week' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  Week
                </button>
                <button
                  onClick={() => setViewMode('day')}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    viewMode === 'day' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  Day
                </button>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateWeek('prev')}
                className="glass-button"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={goToToday}
                className="glass-button min-w-[80px]"
              >
                Today
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateWeek('next')}
                className="glass-button"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <RosterCalendar
            rosters={rosters}
            crews={crews}
            flights={flights}
            currentWeek={currentWeek}
            viewMode={viewMode}
          />
        </CardContent>
      </Card>

      {/* Active Violations Panel */}
      {violations > 0 && (
        <Card className="glass-card border-destructive/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-destructive">
              <Calendar className="h-5 w-5" />
              <span>Active Violations ({violations})</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {rosters
                .filter(roster => roster.violations.length > 0)
                .map(roster => {
                  const crew = crews.find(c => c.id === roster.crewId);
                  return roster.violations.map((violation, index) => (
                    <div key={`${roster.id}-${index}`} className="glass p-4 rounded-lg border border-destructive/20">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <Badge variant="destructive" className="text-xs">
                              {violation.severity.toUpperCase()}
                            </Badge>
                            <span className="text-sm font-medium text-foreground">
                              {crew ? `${crew.firstName} ${crew.lastName}` : 'Unknown Crew'}
                            </span>
                          </div>
                          <p className="text-sm text-foreground mb-1">{violation.description}</p>
                          <p className="text-xs text-muted-foreground">{violation.recommendation}</p>
                        </div>
                        <Button size="sm" variant="outline" className="glass-button">
                          Resolve
                        </Button>
                      </div>
                    </div>
                  ));
                })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Roster;