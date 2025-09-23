import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { User, MapPin, Clock, Plane } from 'lucide-react';
import { Crew } from '@/api/crews';

interface CrewCardProps {
  crew: Crew;
}

const CrewCard: React.FC<CrewCardProps> = ({ crew }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-success/10 text-success border-success/20';
      case 'on_leave': return 'bg-warning/10 text-warning border-warning/20';
      case 'sick_leave': return 'bg-destructive/10 text-destructive border-destructive/20';
      default: return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  return (
    <Card className="glass-card smooth-hover">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium text-foreground">{crew.firstName} {crew.lastName}</h3>
              <p className="text-sm text-muted-foreground">{crew.employeeNumber}</p>
            </div>
          </div>
          <Badge className={getStatusColor(crew.status)}>
            {crew.status.replace('_', ' ')}
          </Badge>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex items-center space-x-2">
            <Plane className="h-4 w-4 text-muted-foreground" />
            <span className="text-foreground">{crew.position}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{crew.homeBase}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">{crew.totalHours}h total</span>
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-border/20">
          <div className="flex flex-wrap gap-1">
            {crew.qualifications.slice(0, 3).map((qual, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {qual}
              </Badge>
            ))}
            {crew.qualifications.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{crew.qualifications.length - 3}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CrewCard;