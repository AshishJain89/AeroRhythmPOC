import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  AlertTriangle, 
  Plus, 
  Filter, 
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  Zap,
  Plane,
  Users
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { crewsApi } from '@/api/crews';
import { rostersApi, DisruptionRequest } from '@/api/rosters';
import DisruptionsFeed from '@/components/DisruptionsFeed';
import { format } from 'date-fns/format';

const Disruptions = () => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: disruptions = [], isLoading } = useQuery({
    queryKey: ['disruptions'],
    queryFn: crewsApi.getDisruptions,
  });

  const { data: crews = [] } = useQuery({
    queryKey: ['crews'],
    queryFn: crewsApi.getCrews,
  });

  const { data: flights = [] } = useQuery({
    queryKey: ['flights'],
    queryFn: crewsApi.getFlights,
  });

  const handleDisruptionMutation = useMutation({
    mutationFn: rostersApi.handleDisruption,
    onSuccess: (response) => {
      toast({
        title: "Disruption Handled",
        description: `Generated ${response.recommendations.length} recommendations for resolution.`,
      });
      queryClient.invalidateQueries({ queryKey: ['disruptions'] });
      queryClient.invalidateQueries({ queryKey: ['rosters'] });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to handle disruption. Please try again.",
        variant: "destructive",
      });
    },
  });

  // Filter disruptions
  const filteredDisruptions = disruptions.filter(disruption => {
    const matchesStatus = statusFilter === 'all' || disruption.status === statusFilter;
    const matchesSeverity = severityFilter === 'all' || disruption.severity === severityFilter;
    return matchesStatus && matchesSeverity;
  });

  // Calculate statistics
  const activeDisruptions = disruptions.filter(d => d.status === 'active').length;
  const criticalDisruptions = disruptions.filter(d => d.severity === 'critical').length;
  const resolvedToday = disruptions.filter(d => {
    const today = new Date().toDateString();
    return d.status === 'resolved' && new Date(d.updatedAt).toDateString() === today;
  }).length;
  const avgResolutionTime = '2.4h'; // Mock data

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'active', label: 'Active' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'scheduled', label: 'Scheduled' },
  ];

  const severityOptions = [
    { value: 'all', label: 'All Severity' },
    { value: 'critical', label: 'Critical' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  const handleApplyDisruption = (disruptionId: string) => {
    const disruption = disruptions.find((d) => d.id === disruptionId);
    if (disruption) {
      handleDisruptionMutation.mutate({
        type: disruption.type as DisruptionRequest['type'],
        affected: [...disruption.affectedFlights, ...disruption.affectedCrew],
        severity: disruption.severity,
        description: disruption.description,
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-destructive';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-warning';
      case 'low': return 'text-muted-foreground';
      default: return 'text-foreground';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Clock className="h-4 w-4 text-warning" />;
      case 'resolved': return <CheckCircle className="h-4 w-4 text-success" />;
      case 'scheduled': return <AlertTriangle className="h-4 w-4 text-primary" />;
      default: return <XCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="glass-card p-8">
          <div className="space-y-4 animate-pulse">
            <div className="h-6 bg-muted rounded w-1/3"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-24 bg-muted rounded-lg"></div>
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
          <h1 className="text-2xl font-bold text-foreground">Disruptions & Alerts</h1>
          <p className="text-muted-foreground">
            Monitor and manage operational disruptions in real-time
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="glass-button"
            onClick={() => queryClient.invalidateQueries({ queryKey: ['disruptions'] })}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button className="glass-button bg-primary hover:bg-primary/90">
            <Plus className="h-4 w-4 mr-2" />
            Report Disruption
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold text-warning">{activeDisruptions}</p>
              </div>
              <Clock className="h-8 w-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Critical</p>
                <p className="text-2xl font-bold text-destructive">{criticalDisruptions}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-destructive" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Resolved Today</p>
                <p className="text-2xl font-bold text-success">{resolvedToday}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Resolution</p>
                <p className="text-2xl font-bold text-accent">{avgResolutionTime}</p>
              </div>
              <Zap className="h-8 w-8 text-accent" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="glass-card">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
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
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="glass px-3 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {severityOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <Button variant="outline" size="sm" className="glass-button">
                <Filter className="h-4 w-4" />
              </Button>
            </div>

            <p className="text-sm text-muted-foreground">
              Showing {filteredDisruptions.length} of {disruptions.length} disruptions
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Disruptions Feed */}
      <DisruptionsFeed
        disruptions={filteredDisruptions}
        crews={crews}
        flights={flights}
        onApplyDisruption={handleApplyDisruption}
        isApplying={handleDisruptionMutation.isPending}
      />

      {/* Empty State */}
      {filteredDisruptions.length === 0 && (
        <Card className="glass-card">
          <CardContent className="p-12 text-center">
            <CheckCircle className="h-12 w-12 text-success mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              {statusFilter === 'all' ? 'No disruptions found' : 'No disruptions with current filters'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {statusFilter === 'all' 
                ? 'All systems are operating normally. Great job!'
                : 'Try adjusting your filters to see more disruptions.'
              }
            </p>
            {statusFilter !== 'all' && (
              <Button
                variant="outline"
                onClick={() => {
                  setStatusFilter('all');
                  setSeverityFilter('all');
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

export default Disruptions;
