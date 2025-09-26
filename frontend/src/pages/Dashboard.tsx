import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Users, 
  Plane, 
  AlertTriangle, 
  Clock, 
  TrendingUp,
  Activity,
  Shield,
  Calendar
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  LineChart, 
  Line 
} from 'recharts';

// import { crewsApi } from '@/api/crews';
// import { rostersApi } from '@/api/rosters';
import { api } from '@/api/apiClient';
import { format } from 'date-fns/format';
import { startOfWeek } from 'date-fns/startOfWeek';
import { endOfWeek } from 'date-fns/endOfWeek';

// Mock data for charts
const utilizationData = [
  { day: 'Mon', utilization: 85, capacity: 100 },
  { day: 'Tue', utilization: 92, capacity: 100 },
  { day: 'Wed', utilization: 78, capacity: 100 },
  { day: 'Thu', utilization: 95, capacity: 100 },
  { day: 'Fri', utilization: 88, capacity: 100 },
  { day: 'Sat', utilization: 76, capacity: 100 },
  { day: 'Sun', utilization: 82, capacity: 100 },
];

const flightStatusData = [
  { name: 'On Time', value: 156, color: '#22c55e' },
  { name: 'Delayed', value: 12, color: '#f59e0b' },
  { name: 'Cancelled', value: 3, color: '#ef4444' },
  { name: 'Unassigned', value: 8, color: '#6b7280' },
];

const performanceData = [
  { metric: 'Avg Assignment Confidence', value: 87 },
  { metric: 'Compliance Score', value: 94 },
  { metric: 'Crew Satisfaction', value: 82 },
  { metric: 'On-Time Performance', value: 91 },
];

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { data: crews = [], isLoading: crewsLoading, error: crewsError } = useQuery({
    queryKey: ['crews'],
    queryFn: () => api.getCrews(),
    retry: 1,
  });
  
  const { data: flights = [], isLoading: flightsLoading, error: flightsError } = useQuery({
    queryKey: ['flights'],
    queryFn: () => api.getFlights(),
    retry: 1,
  });
  
  const { data: disruptions = [], isLoading: disruptionsLoading, error: disruptionsError } = useQuery({
    queryKey: ['disruptions'],
    queryFn: () => api.getDisruptions(),
    retry: 1,
  });
  
  // Add similar error handling for other queries...
  
  const { data: rosters = [], isLoading: rostersLoading, error: rostersError } = useQuery({
    queryKey: ['rosters', 'current-week'],
    queryFn: () => api.getRosters(
      format(startOfWeek(new Date()), 'yyyy-MM-dd'),
      format(endOfWeek(new Date()), 'yyyy-MM-dd')
    ),
    retry: 1,
  });
  
  useEffect(() => {
    if (crewsError || flightsError || disruptionsError || rostersError) {
      setError('Failed to load dashboard data');
    }
    
    if (!crewsLoading && !flightsLoading && !disruptionsLoading && !rostersLoading) {
      setLoading(false);
    }
  }, [
    crewsLoading, flightsLoading, disruptionsLoading, rostersLoading, 
    crewsError, flightsError, disruptionsError, rostersError
  ]);
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-destructive mx-auto" />
          <h2 className="text-2xl font-bold mt-4">Failed to load dashboard</h2>
          <p className="text-muted-foreground mt-2">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg"
            >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  // Your existing dashboard JSX...

  // Calculate metrics
  const availableCrew = crews?.filter(c => c.status === 'available').length || 0;
  const activeFlights = flights?.filter(f => f.status === 'scheduled').length || 0;
  const activeDisruptions = disruptions?.filter(d => d.status === 'active').length || 0;
  const avgUtilization = utilizationData.reduce((acc, day) => acc + day.utilization, 0) / utilizationData.length;

  // Add safe array access
  const totalCrews = crews?.length || 0;
  const crewProgress = totalCrews > 0 ? (availableCrew / totalCrews) * 100 : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Operations Dashboard</h1>
          <p className="text-muted-foreground">Real-time overview of crew operations and system performance</p>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse-glow"></div>
          <span className="text-muted-foreground">Last updated: {format(new Date(), 'HH:mm:ss')}</span>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass-card smooth-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Available Crew</CardTitle>
            <Users className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-success">{availableCrew}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-success">+5</span> from yesterday
            </p>
            <Progress value={(availableCrew / crews.length) * 100} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="glass-card smooth-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Flights</CardTitle>
            <Plane className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{activeFlights}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-primary">24</span> scheduled today
            </p>
            <div className="flex items-center mt-2">
              <TrendingUp className="h-3 w-3 text-success mr-1" />
              <span className="text-xs text-success">+8% from last week</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card smooth-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Disruptions</CardTitle>
            <AlertTriangle className="h-4 w-4 text-warning" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning">{activeDisruptions}</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-warning">2</span> critical, <span className="text-accent">1</span> medium
            </p>
            {activeDisruptions > 0 && (
              <Badge variant="outline" className="mt-2 text-xs">
                Action Required
              </Badge>
            )}
          </CardContent>
        </Card>

        <Card className="glass-card smooth-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Crew Utilization</CardTitle>
            <Activity className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-accent">{Math.round(avgUtilization)}%</div>
            <p className="text-xs text-muted-foreground">
              Weekly average
            </p>
            <Progress value={avgUtilization} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Utilization Chart */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-primary" />
              <span>Weekly Crew Utilization</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={utilizationData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="day" className="text-xs" />
                <YAxis className="text-xs" />
                <Bar dataKey="utilization" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Flight Status Distribution */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-success" />
              <span>Flight Status Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={flightStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {flightStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-2 gap-2 mt-4">
              {flightStatusData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-xs text-muted-foreground">{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-accent" />
            <span>System Performance Metrics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {performanceData.map((metric, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">{metric.metric}</span>
                  <span className="text-sm font-bold text-primary">{metric.value}%</span>
                </div>
                <Progress value={metric.value} className="h-2" />
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Updated 5m ago</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="glass-card lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { time: '2 minutes ago', action: 'Flight 6E-2041 crew assigned', status: 'success' },
                { time: '5 minutes ago', action: 'Weather delay reported for DEL departures', status: 'warning' },
                { time: '12 minutes ago', action: 'Crew member Rajesh Sharma returned from leave', status: 'info' },
                { time: '18 minutes ago', action: 'Technical issue resolved for VT-IJL', status: 'success' },
                { time: '25 minutes ago', action: 'Roster optimization completed', status: 'success' },
              ].map((activity, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 glass rounded-lg">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.status === 'success' ? 'bg-success' :
                    activity.status === 'warning' ? 'bg-warning' :
                    'bg-primary'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-foreground">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
              <div className="font-medium text-sm">Generate New Roster</div>
              <div className="text-xs text-muted-foreground">Create optimized crew assignments</div>
            </button>
            
            <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
              <div className="font-medium text-sm">Handle Disruption</div>
              <div className="text-xs text-muted-foreground">Report and manage disruptions</div>
            </button>
            
            <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
              <div className="font-medium text-sm">Crew Availability</div>
              <div className="text-xs text-muted-foreground">Check crew status and availability</div>
            </button>
            
            <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
              <div className="font-medium text-sm">Export Reports</div>
              <div className="text-xs text-muted-foreground">Generate operational reports</div>
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// const Dashboard = () => {
  // const { data: crews = [] } = useQuery({
  //   queryKey: ['crews'],
  //   queryFn: api.getCrews,
  // });

  // const { data: flights = [] } = useQuery({
  //   queryKey: ['flights'],
  //   queryFn: api.getFlights,
  // });

  // const { data: disruptions = [] } = useQuery({
  //   queryKey: ['disruptions'],
  //   queryFn: api.getDisruptions,
  // });

  // const { data: rostersData } = useQuery({
  //   queryKey: ['rosters', 'current-week'],
  //   queryFn: () => api.getRosters(
  //     format(startOfWeek(new Date()), 'yyyy-MM-dd'),
  //     format(endOfWeek(new Date()), 'yyyy-MM-dd')
  //   ),
  // });

  // // Calculate metrics
  // const availableCrew = crews.filter(c => c.status === 'available').length;
  // const activeFlights = flights.filter(f => f.status === 'scheduled').length;
  // const activeDisruptions = disruptions.filter(d => d.status === 'active').length;
  // const avgUtilization = utilizationData.reduce((acc, day) => acc + day.utilization, 0) / utilizationData.length;

  // return (
  //   <div className="space-y-6 animate-fade-in">
  //     {/* Header */}
  //     <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
  //       <div>
  //         <h1 className="text-2xl font-bold text-foreground">Operations Dashboard</h1>
  //         <p className="text-muted-foreground">Real-time overview of crew operations and system performance</p>
  //       </div>
  //       <div className="flex items-center space-x-2 text-sm">
  //         <div className="w-2 h-2 bg-success rounded-full animate-pulse-glow"></div>
  //         <span className="text-muted-foreground">Last updated: {format(new Date(), 'HH:mm:ss')}</span>
  //       </div>
  //     </div>

  //     {/* Key Metrics Cards */}
  //     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  //       <Card className="glass-card smooth-hover">
  //         <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
  //           <CardTitle className="text-sm font-medium">Available Crew</CardTitle>
  //           <Users className="h-4 w-4 text-success" />
  //         </CardHeader>
  //         <CardContent>
  //           <div className="text-2xl font-bold text-success">{availableCrew}</div>
  //           <p className="text-xs text-muted-foreground">
  //             <span className="text-success">+5</span> from yesterday
  //           </p>
  //           <Progress value={(availableCrew / crews.length) * 100} className="mt-2" />
  //         </CardContent>
  //       </Card>

  //       <Card className="glass-card smooth-hover">
  //         <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
  //           <CardTitle className="text-sm font-medium">Active Flights</CardTitle>
  //           <Plane className="h-4 w-4 text-primary" />
  //         </CardHeader>
  //         <CardContent>
  //           <div className="text-2xl font-bold text-primary">{activeFlights}</div>
  //           <p className="text-xs text-muted-foreground">
  //             <span className="text-primary">24</span> scheduled today
  //           </p>
  //           <div className="flex items-center mt-2">
  //             <TrendingUp className="h-3 w-3 text-success mr-1" />
  //             <span className="text-xs text-success">+8% from last week</span>
  //           </div>
  //         </CardContent>
  //       </Card>

  //       <Card className="glass-card smooth-hover">
  //         <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
  //           <CardTitle className="text-sm font-medium">Active Disruptions</CardTitle>
  //           <AlertTriangle className="h-4 w-4 text-warning" />
  //         </CardHeader>
  //         <CardContent>
  //           <div className="text-2xl font-bold text-warning">{activeDisruptions}</div>
  //           <p className="text-xs text-muted-foreground">
  //             <span className="text-warning">2</span> critical, <span className="text-accent">1</span> medium
  //           </p>
  //           {activeDisruptions > 0 && (
  //             <Badge variant="outline" className="mt-2 text-xs">
  //               Action Required
  //             </Badge>
  //           )}
  //         </CardContent>
  //       </Card>

  //       <Card className="glass-card smooth-hover">
  //         <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
  //           <CardTitle className="text-sm font-medium">Crew Utilization</CardTitle>
  //           <Activity className="h-4 w-4 text-accent" />
  //         </CardHeader>
  //         <CardContent>
  //           <div className="text-2xl font-bold text-accent">{Math.round(avgUtilization)}%</div>
  //           <p className="text-xs text-muted-foreground">
  //             Weekly average
  //           </p>
  //           <Progress value={avgUtilization} className="mt-2" />
  //         </CardContent>
  //       </Card>
  //     </div>

  //     {/* Charts Section */}
  //     <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  //       {/* Weekly Utilization Chart */}
  //       <Card className="glass-card">
  //         <CardHeader>
  //           <CardTitle className="flex items-center space-x-2">
  //             <Calendar className="h-5 w-5 text-primary" />
  //             <span>Weekly Crew Utilization</span>
  //           </CardTitle>
  //         </CardHeader>
  //         <CardContent>
  //           <ResponsiveContainer width="100%" height={250}>
  //             <BarChart data={utilizationData}>
  //               <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
  //               <XAxis dataKey="day" className="text-xs" />
  //               <YAxis className="text-xs" />
  //               <Bar dataKey="utilization" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
  //             </BarChart>
  //           </ResponsiveContainer>
  //         </CardContent>
  //       </Card>

  //       {/* Flight Status Distribution */}
  //       <Card className="glass-card">
  //         <CardHeader>
  //           <CardTitle className="flex items-center space-x-2">
  //             <Shield className="h-5 w-5 text-success" />
  //             <span>Flight Status Distribution</span>
  //           </CardTitle>
  //         </CardHeader>
  //         <CardContent>
  //           <ResponsiveContainer width="100%" height={250}>
  //             <PieChart>
  //               <Pie
  //                 data={flightStatusData}
  //                 cx="50%"
  //                 cy="50%"
  //                 innerRadius={60}
  //                 outerRadius={100}
  //                 paddingAngle={5}
  //                 dataKey="value"
  //               >
  //                 {flightStatusData.map((entry, index) => (
  //                   <Cell key={`cell-${index}`} fill={entry.color} />
  //                 ))}
  //               </Pie>
  //             </PieChart>
  //           </ResponsiveContainer>
  //           <div className="grid grid-cols-2 gap-2 mt-4">
  //             {flightStatusData.map((item, index) => (
  //               <div key={index} className="flex items-center space-x-2">
  //                 <div 
  //                   className="w-3 h-3 rounded-full" 
  //                   style={{ backgroundColor: item.color }}
  //                 />
  //                 <span className="text-xs text-muted-foreground">{item.name}: {item.value}</span>
  //               </div>
  //             ))}
  //           </div>
  //         </CardContent>
  //       </Card>
  //     </div>

  //     {/* Performance Metrics */}
  //     <Card className="glass-card">
  //       <CardHeader>
  //         <CardTitle className="flex items-center space-x-2">
  //           <TrendingUp className="h-5 w-5 text-accent" />
  //           <span>System Performance Metrics</span>
  //         </CardTitle>
  //       </CardHeader>
  //       <CardContent>
  //         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  //           {performanceData.map((metric, index) => (
  //             <div key={index} className="space-y-2">
  //               <div className="flex items-center justify-between">
  //                 <span className="text-sm font-medium text-foreground">{metric.metric}</span>
  //                 <span className="text-sm font-bold text-primary">{metric.value}%</span>
  //               </div>
  //               <Progress value={metric.value} className="h-2" />
  //               <div className="flex items-center space-x-1">
  //                 <Clock className="h-3 w-3 text-muted-foreground" />
  //                 <span className="text-xs text-muted-foreground">Updated 5m ago</span>
  //               </div>
  //             </div>
  //           ))}
  //         </div>
  //       </CardContent>
  //     </Card>

  //     {/* Recent Activity & Quick Actions */}
  //     <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  //       {/* Recent Activity */}
  //       <Card className="glass-card lg:col-span-2">
  //         <CardHeader>
  //           <CardTitle>Recent Activity</CardTitle>
  //         </CardHeader>
  //         <CardContent>
  //           <div className="space-y-4">
  //             {[
  //               { time: '2 minutes ago', action: 'Flight 6E-2041 crew assigned', status: 'success' },
  //               { time: '5 minutes ago', action: 'Weather delay reported for DEL departures', status: 'warning' },
  //               { time: '12 minutes ago', action: 'Crew member Rajesh Sharma returned from leave', status: 'info' },
  //               { time: '18 minutes ago', action: 'Technical issue resolved for VT-IJL', status: 'success' },
  //               { time: '25 minutes ago', action: 'Roster optimization completed', status: 'success' },
  //             ].map((activity, index) => (
  //               <div key={index} className="flex items-start space-x-3 p-3 glass rounded-lg">
  //                 <div className={`w-2 h-2 rounded-full mt-2 ${
  //                   activity.status === 'success' ? 'bg-success' :
  //                   activity.status === 'warning' ? 'bg-warning' :
  //                   'bg-primary'
  //                 }`} />
  //                 <div className="flex-1 min-w-0">
  //                   <p className="text-sm text-foreground">{activity.action}</p>
  //                   <p className="text-xs text-muted-foreground">{activity.time}</p>
  //                 </div>
  //               </div>
  //             ))}
  //           </div>
  //         </CardContent>
  //       </Card>

  //       {/* Quick Actions */}
  //       <Card className="glass-card">
  //         <CardHeader>
  //           <CardTitle>Quick Actions</CardTitle>
  //         </CardHeader>
  //         <CardContent className="space-y-3">
  //           <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
  //             <div className="font-medium text-sm">Generate New Roster</div>
  //             <div className="text-xs text-muted-foreground">Create optimized crew assignments</div>
  //           </button>
            
  //           <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
  //             <div className="font-medium text-sm">Handle Disruption</div>
  //             <div className="text-xs text-muted-foreground">Report and manage disruptions</div>
  //           </button>
            
  //           <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
  //             <div className="font-medium text-sm">Crew Availability</div>
  //             <div className="text-xs text-muted-foreground">Check crew status and availability</div>
  //           </button>
            
  //           <button className="w-full glass-button p-3 rounded-lg text-left hover:bg-primary/5 transition-colors">
  //             <div className="font-medium text-sm">Export Reports</div>
  //             <div className="text-xs text-muted-foreground">Generate operational reports</div>
  //           </button>
  //         </CardContent>
  //       </Card>
  //     </div>
  //   </div>
  // );
// };

export default Dashboard;
