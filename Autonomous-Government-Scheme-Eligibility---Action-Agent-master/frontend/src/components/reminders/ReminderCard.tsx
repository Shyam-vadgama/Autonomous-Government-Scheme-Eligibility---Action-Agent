import { Reminder } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar, Bell, FileText, RefreshCw, Clock, Check, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { format, parseISO, isAfter, isBefore, addDays } from 'date-fns';

interface ReminderCardProps {
  reminder: Reminder;
  onComplete: (id: string) => void;
}

export function ReminderCard({ reminder, onComplete }: ReminderCardProps) {
  const typeConfig = {
    deadline: { 
      icon: Clock, 
      color: 'text-destructive', 
      bg: 'bg-destructive/10',
      border: 'border-destructive/20',
      label: 'Deadline'
    },
    'follow-up': { 
      icon: Bell, 
      color: 'text-info', 
      bg: 'bg-info/10',
      border: 'border-info/20',
      label: 'Follow-up'
    },
    document: { 
      icon: FileText, 
      color: 'text-warning', 
      bg: 'bg-warning/10',
      border: 'border-warning/20',
      label: 'Document'
    },
    update: { 
      icon: RefreshCw, 
      color: 'text-success', 
      bg: 'bg-success/10',
      border: 'border-success/20',
      label: 'Update'
    },
  };

  const config = typeConfig[reminder.type];
  const TypeIcon = config.icon;
  
  const reminderDate = parseISO(reminder.date);
  const today = new Date();
  const isOverdue = isBefore(reminderDate, today) && reminder.status === 'pending';
  const isUpcoming = isAfter(reminderDate, today) && isBefore(reminderDate, addDays(today, 3));

  return (
    <Card className={cn(
      "transition-all duration-300 hover:shadow-md overflow-hidden border-l-4",
      reminder.status === 'completed' && "opacity-60 border-l-success",
      isOverdue && "border-l-destructive bg-destructive/5",
      !isOverdue && reminder.status === 'pending' && config.border
    )}>
      <CardContent className="p-5">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className={cn(
            "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition-all",
            reminder.status === 'completed' ? 'bg-success/15' : config.bg
          )}>
            {reminder.status === 'completed' ? (
              <Check className="h-6 w-6 text-success" />
            ) : (
              <TypeIcon className={cn("h-6 w-6", config.color)} />
            )}
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge variant="outline" className="text-xs font-medium">
                {config.label}
              </Badge>
              {isOverdue && (
                <Badge variant="destructive" className="gap-1 text-xs">
                  <AlertCircle className="h-3 w-3" />
                  Overdue
                </Badge>
              )}
              {isUpcoming && reminder.status === 'pending' && (
                <Badge variant="warning" className="text-xs">Due Soon</Badge>
              )}
            </div>
            
            <h4 className={cn(
              "font-display text-base font-semibold text-foreground mb-1.5",
              reminder.status === 'completed' && "line-through text-muted-foreground"
            )}>
              {reminder.title}
            </h4>
            
            <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
              {reminder.description}
            </p>
            
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span className="font-medium">{format(reminderDate, 'EEEE, MMMM d, yyyy')}</span>
            </div>
          </div>
          
          {/* Action Button */}
          {reminder.status === 'pending' && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onComplete(reminder.id)}
              className="shrink-0 gap-2 hover:bg-success hover:text-success-foreground hover:border-success"
            >
              <Check className="h-4 w-4" />
              Done
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
