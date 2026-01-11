import { ActionStep } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Clock, CheckCircle2, Circle, Loader2, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ActionStepCardProps {
  step: ActionStep;
  onStatusChange: (id: string, status: ActionStep['status']) => void;
}

export function ActionStepCard({ step, onStatusChange }: ActionStepCardProps) {
  const priorityConfig = {
    high: { label: 'High', variant: 'destructive' as const, dot: 'bg-destructive' },
    medium: { label: 'Medium', variant: 'warning' as const, dot: 'bg-warning' },
    low: { label: 'Low', variant: 'secondary' as const, dot: 'bg-muted-foreground' },
  };

  const statusConfig = {
    pending: {
      icon: Circle,
      label: 'Pending',
      btnLabel: 'Start Task',
      nextStatus: 'in-progress' as const,
      cardClass: 'border-l-muted-foreground/50 bg-card',
      iconClass: 'bg-muted text-muted-foreground',
    },
    'in-progress': {
      icon: Loader2,
      label: 'In Progress',
      btnLabel: 'Mark Complete',
      nextStatus: 'completed' as const,
      cardClass: 'border-l-info bg-info/5',
      iconClass: 'bg-info text-info-foreground',
    },
    completed: {
      icon: CheckCircle2,
      label: 'Completed',
      btnLabel: null,
      nextStatus: null,
      cardClass: 'border-l-success bg-success/5',
      iconClass: 'bg-success text-success-foreground',
    },
  };

  const priority = priorityConfig[step.priority];
  const status = statusConfig[step.status];
  const StatusIcon = status.icon;

  return (
    <Card className={cn(
      "transition-all duration-300 border-l-4 hover:shadow-md overflow-hidden",
      status.cardClass
    )}>
      <CardContent className="p-5">
        <div className="flex items-start gap-4">
          {/* Status Icon */}
          <div className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-all shadow-sm",
            status.iconClass
          )}>
            <StatusIcon className={cn(
              "h-5 w-5", 
              step.status === 'in-progress' && "animate-spin"
            )} />
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <div className={cn("h-2 w-2 rounded-full", priority.dot)} />
              <span className="text-xs font-medium text-muted-foreground">{priority.label} Priority</span>
              <span className="text-muted-foreground/50">•</span>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {step.estimatedTime}
              </span>
            </div>
            
            <h4 className={cn(
              "font-display text-base font-semibold text-foreground mb-1.5 transition-colors",
              step.status === 'completed' && "line-through text-muted-foreground"
            )}>
              Step {step.step}: {step.title}
            </h4>
            
            <p className="text-sm text-muted-foreground leading-relaxed">
              {step.description}
            </p>
          </div>
          
          {/* Action Button */}
          {status.btnLabel && (
            <Button
              size="sm"
              variant={step.status === 'in-progress' ? 'success' : 'outline'}
              onClick={() => status.nextStatus && onStatusChange(step.id, status.nextStatus)}
              className="shrink-0 gap-2"
            >
              {status.btnLabel}
              <ArrowRight className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
