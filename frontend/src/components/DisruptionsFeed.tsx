import { Badge, badgeVariants } from '@/components/ui/badge';
import { VariantProps } from 'class-variance-authority';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { AlertTriangle, Clock, Zap } from 'lucide-react';
import { Disruption, Crew, Flight } from '@/api/crews';
import { format } from 'date-fns/format';

interface DisruptionsFeedProps {
  disruptions: Disruption[];
  crews: Crew[];
  flights: Flight[];
  onApplyDisruption: (disruptionId: string) => void;
  isApplying: boolean;
}

type BadgeVariant = VariantProps<typeof badgeVariants>['variant'];

const DisruptionsFeed: React.FC<DisruptionsFeedProps> = ({
  disruptions,
  onApplyDisruption,
  isApplying,
}) => {
  const getSeverityColor = (severity: string): BadgeVariant => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  return (
    <div className="space-y-4">
      {disruptions.map((disruption) => (
        <Card key={disruption.id} className="glass-card">
          <CardContent className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start space-x-3">
                <div className="flex items-center justify-center w-10 h-10 bg-warning/10 rounded-full">
                  <AlertTriangle className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <h3 className="font-medium text-foreground mb-1">{disruption.title}</h3>
                  <p className="text-sm text-muted-foreground">{disruption.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant={getSeverityColor(disruption.severity)}>
                  {disruption.severity.toUpperCase()}
                </Badge>
                <Badge variant="outline">
                  {disruption.status}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  {format(new Date(disruption.startTime), 'MMM dd, HH:mm')}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">Affected Flights: </span>
                <span className="text-foreground">{disruption.affectedFlights.length}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">Affected Crew: </span>
                <span className="text-foreground">{disruption.affectedCrew.length}</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-accent" />
                <span className="text-sm text-muted-foreground">
                  Impact: {disruption.impactAssessment.passengerImpact}
                </span>
              </div>
              
              {disruption.status === 'active' && (
                <Button
                  onClick={() => onApplyDisruption(disruption.id)}
                  disabled={isApplying}
                  className="glass-button bg-primary hover:bg-primary/90"
                >
                  {isApplying ? 'Processing...' : 'Recalculate'}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DisruptionsFeed;
