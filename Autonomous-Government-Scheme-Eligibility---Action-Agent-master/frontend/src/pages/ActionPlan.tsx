import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { ActionStepCard } from '@/components/action-plan/ActionStepCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { mockActionSteps, ActionStep } from '@/lib/mockData';
import { ClipboardList, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

export default function ActionPlan() {
  const [steps, setSteps] = useState<ActionStep[]>(mockActionSteps);

  const handleStatusChange = (id: string, newStatus: ActionStep['status']) => {
    setSteps(prev => prev.map(step => 
      step.id === id ? { ...step, status: newStatus } : step
    ));
  };

  const completedCount = steps.filter(s => s.status === 'completed').length;
  const inProgressCount = steps.filter(s => s.status === 'in-progress').length;
  const pendingCount = steps.filter(s => s.status === 'pending').length;
  const progressPercent = (completedCount / steps.length) * 100;

  // Group steps by scheme
  const groupedSteps = steps.reduce((acc, step) => {
    if (!acc[step.schemeName]) {
      acc[step.schemeName] = [];
    }
    acc[step.schemeName].push(step);
    return acc;
  }, {} as Record<string, ActionStep[]>);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-2">
            Your Action Plan
          </h1>
          <p className="text-muted-foreground">
            Follow these steps to apply for your eligible schemes. Complete tasks in order for best results.
          </p>
        </div>

        {/* Progress Overview */}
        <Card className="mb-8 shadow-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5 text-primary" />
              Overall Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  {completedCount} of {steps.length} steps completed
                </span>
                <span className="font-semibold text-primary">{Math.round(progressPercent)}%</span>
              </div>
              <Progress value={progressPercent} className="h-3" />
              
              <div className="grid grid-cols-3 gap-4 pt-4">
                <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <div>
                    <p className="font-semibold text-foreground">{completedCount}</p>
                    <p className="text-xs text-muted-foreground">Completed</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                  <Clock className="h-5 w-5 text-info" />
                  <div>
                    <p className="font-semibold text-foreground">{inProgressCount}</p>
                    <p className="text-xs text-muted-foreground">In Progress</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg">
                  <AlertCircle className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-semibold text-foreground">{pendingCount}</p>
                    <p className="text-xs text-muted-foreground">Pending</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Grouped Action Steps */}
        <div className="space-y-8">
          {Object.entries(groupedSteps).map(([schemeName, schemeSteps]) => (
            <div key={schemeName} className="animate-fade-in">
              <div className="flex items-center gap-3 mb-4">
                <Badge variant="category" className="text-sm">{schemeName}</Badge>
                <span className="text-sm text-muted-foreground">
                  {schemeSteps.filter(s => s.status === 'completed').length} of {schemeSteps.length} completed
                </span>
              </div>
              
              <div className="space-y-3 relative">
                {/* Timeline Line */}
                <div className="absolute left-[1.35rem] top-4 bottom-4 w-0.5 bg-border" />
                
                {schemeSteps.map((step, index) => (
                  <div key={step.id} style={{ animationDelay: `${index * 100}ms` }} className="animate-fade-in">
                    <ActionStepCard step={step} onStatusChange={handleStatusChange} />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
