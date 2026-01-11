import { Scheme } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { CheckCircle2, XCircle, AlertTriangle, FileText, Check, X, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';

interface SchemeDetailModalProps {
  scheme: Scheme | null;
  open: boolean;
  onClose: () => void;
}

export function SchemeDetailModal({ scheme, open, onClose }: SchemeDetailModalProps) {
  const { user } = useAuth();
  
  if (!scheme) return null;

  const statusConfig = {
    eligible: {
      icon: CheckCircle2,
      label: 'Eligible',
      variant: 'eligible' as const,
      textClass: 'text-success',
      bgClass: 'bg-success/10',
    },
    rejected: {
      icon: XCircle,
      label: 'Not Eligible',
      variant: 'rejected' as const,
      textClass: 'text-destructive',
      bgClass: 'bg-destructive/10',
    },
    conditional: {
      icon: AlertTriangle,
      label: 'Conditional',
      variant: 'conditional' as const,
      textClass: 'text-warning',
      bgClass: 'bg-warning/10',
    },
  };

  const config = statusConfig[scheme.status];
  const StatusIcon = config.icon;

  const availableCount = scheme.requiredDocuments.filter(d => d.available).length;
  const totalCount = scheme.requiredDocuments.length;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <Badge variant="category" className="mb-2">{scheme.category}</Badge>
              <DialogTitle className="font-display text-2xl">{scheme.name}</DialogTitle>
            </div>
            <Badge variant={config.variant} className="flex items-center gap-1.5 shrink-0">
              <StatusIcon className="h-4 w-4" />
              {config.label}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Description */}
          <div>
            <h4 className="font-semibold text-foreground mb-2">About this Scheme</h4>
            <p className="text-muted-foreground">{scheme.description}</p>
          </div>

          {/* Benefits */}
          <div className={cn("p-4 rounded-lg", config.bgClass)}>
            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
              <Info className="h-4 w-4" />
              Benefits
            </h4>
            <p className={cn("font-medium", config.textClass)}>{scheme.benefits}</p>
          </div>

          {/* Eligibility Decision */}
          <div className="border border-border rounded-lg p-4">
            <h4 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <StatusIcon className={cn("h-5 w-5", config.textClass)} />
              Eligibility Decision
            </h4>
            <p className="text-muted-foreground">{scheme.reason}</p>
            
            {scheme.conditionalNote && (
              <div className="mt-4 p-3 bg-warning/10 border border-warning/20 rounded-lg">
                <p className="text-sm text-warning font-medium">
                  <AlertTriangle className="h-4 w-4 inline mr-2" />
                  {scheme.conditionalNote}
                </p>
              </div>
            )}
          </div>

          {/* Required Documents */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-foreground flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Required Documents
              </h4>
              <span className="text-sm text-muted-foreground">
                {availableCount} of {totalCount} available
              </span>
            </div>
            
            <div className="space-y-2">
              {scheme.requiredDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-lg border transition-colors",
                    doc.available
                      ? "bg-success/5 border-success/20"
                      : "bg-muted border-border"
                  )}
                >
                  <div className="flex items-center gap-3">
                    {doc.available ? (
                      <Check className="h-5 w-5 text-success" />
                    ) : (
                      <X className="h-5 w-5 text-muted-foreground" />
                    )}
                    <span className={cn(
                      "font-medium",
                      doc.available ? "text-foreground" : "text-muted-foreground"
                    )}>
                      {doc.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {doc.mandatory && (
                      <Badge variant="destructive" className="text-xs">Required</Badge>
                    )}
                    {doc.available ? (
                      <Badge variant="success" className="text-xs">Available</Badge>
                    ) : (
                      <Badge variant="secondary" className="text-xs">Missing</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Close
            </Button>
            {scheme.status !== 'rejected' && (
              <Button 
                variant="hero" 
                className="flex-1"
                onClick={() => {
                  if (scheme.applicationUrl) {
                    const url = new URL(scheme.applicationUrl);
                    if (user?.id) {
                      url.searchParams.append('user_id', user.id);
                    }
                    window.open(url.toString(), '_blank');
                  } else {
                    // Fallback or handle cases with no URL
                    console.log("No application URL available");
                  }
                }}
              >
                Start Application
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
