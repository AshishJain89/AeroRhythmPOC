import { Badge } from '@/components/ui/badge';
import { format, startOfWeek, addDays } from 'date-fns';
import { Roster } from '@/api/rosters';
import { Crew, Flight } from '@/api/crews';

interface RosterCalendarProps {
  rosters: Roster[];
  crews: Crew[];
  flights: Flight[];
  currentWeek: Date;
  viewMode: 'week' | 'day';
}

const RosterCalendar: React.FC<RosterCalendarProps> = ({
  rosters,
  crews,
  flights,
  currentWeek,
  viewMode
}) => {
  const weekStart = startOfWeek(currentWeek);
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  const getCrewName = (crewId: string) => {
    const crew = crews.find(c => c.id === crewId);
    return crew ? `${crew.firstName} ${crew.lastName}` : 'Unknown';
  };

  const getFlightDetails = (flightId: string | null) => {
    if (!flightId) return null;
    const flight = flights.find(f => f.id === flightId);
    return flight;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-success/10 text-success border-success/20';
      case 'tentative': return 'bg-warning/10 text-warning border-warning/20';
      case 'cancelled': return 'bg-destructive/10 text-destructive border-destructive/20';
      default: return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  return (
    <div className="space-y-4">
      {/* Week Header */}
      <div className="grid grid-cols-8 gap-2 mb-4">
        <div className="text-sm font-medium text-muted-foreground">Crew</div>
        {days.map((day, index) => (
          <div key={index} className="text-center">
            <div className="text-sm font-medium text-foreground">
              {format(day, 'EEE')}
            </div>
            <div className="text-xs text-muted-foreground">
              {format(day, 'MMM dd')}
            </div>
          </div>
        ))}
      </div>

      {/* Roster Rows */}
      <div className="space-y-2">
        {crews.map((crew) => {
          const crewRosters = rosters.filter(r => r.crewId === crew.id);
          
          return (
            <div key={crew.id} className="grid grid-cols-8 gap-2 py-2 glass rounded-lg">
              <div className="flex items-center space-x-2 px-3">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <span className="text-xs font-medium text-primary">
                    {crew.firstName.charAt(0)}{crew.lastName.charAt(0)}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-foreground">
                    {crew.firstName} {crew.lastName}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {crew.position}
                  </div>
                </div>
              </div>

              {days.map((day, dayIndex) => {
                const dayRosters = crewRosters.filter(roster => {
                  const rosterDate = new Date(roster.startTime);
                  return rosterDate.toDateString() === day.toDateString();
                });

                return (
                  <div key={dayIndex} className="min-h-[60px] flex flex-col space-y-1">
                    {dayRosters.map((roster) => {
                      const flight = getFlightDetails(roster.flightId);
                      
                      return (
                        <div
                          key={roster.id}
                          className={`p-2 rounded text-xs border ${getStatusColor(roster.status)} cursor-pointer hover:scale-105 transition-transform`}
                        >
                          {flight ? (
                            <>
                              <div className="font-medium">{flight.flightNumber}</div>
                              <div className="text-xs opacity-75">
                                {flight.route.origin}-{flight.route.destination}
                              </div>
                              <div className="text-xs opacity-75">
                                {format(new Date(roster.startTime), 'HH:mm')}
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="font-medium">{roster.dutyType}</div>
                              <div className="text-xs opacity-75">{roster.position}</div>
                            </>
                          )}
                          
                          {roster.violations.length > 0 && (
                            <Badge variant="destructive" className="text-xs mt-1">
                              Violation
                            </Badge>
                          )}
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>

      {rosters.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <p>No roster assignments found for this period.</p>
        </div>
      )}
    </div>
  );
};

export default RosterCalendar;