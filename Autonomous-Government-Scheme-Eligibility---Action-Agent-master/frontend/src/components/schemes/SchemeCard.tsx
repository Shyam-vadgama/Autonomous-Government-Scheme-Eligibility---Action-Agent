import { Scheme } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { CheckCircle2, XCircle, AlertTriangle, ChevronRight, TrendingUp, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SchemeCardProps {
  scheme: Scheme;
  onViewDetails: (scheme: Scheme) => void;
}

export function SchemeCard({ scheme, onViewDetails }: SchemeCardProps) {
  const statusConfig = {
    eligible: {
      icon: CheckCircle2,
      label: 'Eligible',
      variant: 'eligible' as const,
      bgClass: 'bg-gradient-to-br from-success/5 to-success/10 border-success/25 hover:border-success/50',
      iconBg: 'bg-success/15',
      iconColor: 'text-success',
    },
    rejected: {
      icon: XCircle,
      label: 'Not Eligible',
      variant: 'rejected' as const,
      bgClass: 'bg-gradient-to-br from-destructive/5 to-destructive/10 border-destructive/25 hover:border-destructive/50',
      iconBg: 'bg-destructive/15',
      iconColor: 'text-destructive',
    },
    conditional: {
      icon: AlertTriangle,
      label: 'Conditional',
      variant: 'conditional' as const,
      bgClass: 'bg-gradient-to-br from-warning/5 to-warning/10 border-warning/25 hover:border-warning/50',
      iconBg: 'bg-warning/15',
      iconColor: 'text-warning',
    },
  };

  const config = statusConfig[scheme.status];
  const StatusIcon = config.icon;

  return (
    <Card className={cn(
      "group relative overflow-hidden transition-all duration-300 hover:shadow-elevated border-2 hover-lift",
      config.bgClass
    )}>
      {/* Decorative Element */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-primary/5 to-transparent rounded-full -translate-y-1/2 translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <Badge variant="category" className="mb-3 text-xs">{scheme.category}</Badge>
            <h3 className="font-display text-lg font-bold text-foreground group-hover:text-primary transition-colors leading-tight">
              {scheme.name}
            </h3>
          </div>
          <div className={cn(
            "flex items-center justify-center h-10 w-10 rounded-xl shrink-0 transition-transform group-hover:scale-110",
            config.iconBg
          )}>
            <StatusIcon className={cn("h-5 w-5", config.iconColor)} />
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-5">
        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
          {scheme.description}
        </p>
        
        <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-xl">
          <Sparkles className="h-4 w-4 text-secondary shrink-0" />
          <div className="flex-1 min-w-0">
            <span className="text-xs text-muted-foreground">Benefits</span>
            <p className="text-sm font-semibold text-foreground truncate">{scheme.benefits}</p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="font-medium text-foreground">Match Score</span>
            </div>
            <span className="font-bold text-primary">{scheme.relevanceScore}%</span>
          </div>
          <div className="h-2.5 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full gradient-hero rounded-full transition-all duration-1000 animate-progress-fill shadow-sm"
              style={{ width: `${scheme.relevanceScore}%` }}
            />
          </div>
        </div>

        <Badge variant={config.variant} className="w-full justify-center py-2 text-sm font-semibold">
          <StatusIcon className="h-4 w-4 mr-2" />
          {config.label}
        </Badge>
      </CardContent>
      
      <CardFooter className="pt-0 pb-5">
        <Button 
          variant="outline" 
          className="w-full group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-all duration-300 font-semibold"
          onClick={() => onViewDetails(scheme)}
        >
          View Details
          <ChevronRight className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" />
        </Button>
      </CardFooter>
    </Card>
  );
}
