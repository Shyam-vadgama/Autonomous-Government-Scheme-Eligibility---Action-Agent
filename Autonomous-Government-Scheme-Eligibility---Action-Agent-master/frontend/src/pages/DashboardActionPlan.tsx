import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ActionStepCard } from '@/components/action-plan/ActionStepCard';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { mockActionSteps } from '@/lib/mockData';
import { useLanguage } from '@/contexts/LanguageContext';
import { CheckCircle2, Clock, PlayCircle } from 'lucide-react';
import { useState } from 'react';

export default function DashboardActionPlan() {
  const { t } = useLanguage();
  const [steps, setSteps] = useState(mockActionSteps);

  const completedCount = steps.filter(s => s.status === 'completed').length;
  const inProgressCount = steps.filter(s => s.status === 'in-progress').length;
  const pendingCount = steps.filter(s => s.status === 'pending').length;
  const progressPercentage = Math.round((completedCount / steps.length) * 100);

  const handleStatusChange = (stepId: string, newStatus: 'pending' | 'in-progress' | 'completed') => {
    setSteps(prev => prev.map(step => 
      step.id === stepId ? { ...step, status: newStatus } : step
    ));
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-6 md:py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground mb-2">
            {t('actionPlan.title')}
          </h1>
          <p className="text-muted-foreground">
            {t('actionPlan.subtitle')}
          </p>
        </div>

        {/* Progress Overview */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-foreground">{t('actionPlan.progress')}</h3>
                  <span className="text-sm text-muted-foreground">
                    {t('actionPlan.stepsCompleted')
                      .replace('{completed}', String(completedCount))
                      .replace('{total}', String(steps.length))}
                  </span>
                </div>
                <Progress value={progressPercentage} className="h-3" />
              </div>

              <div className="flex items-center gap-4 md:gap-6">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-success/10">
                    <CheckCircle2 className="h-4 w-4 text-success" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-foreground">{completedCount}</p>
                    <p className="text-xs text-muted-foreground">{t('actionPlan.completed')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                    <PlayCircle className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-foreground">{inProgressCount}</p>
                    <p className="text-xs text-muted-foreground">{t('actionPlan.inProgress')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-foreground">{pendingCount}</p>
                    <p className="text-xs text-muted-foreground">{t('actionPlan.pending')}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Steps */}
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={step.id} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
              <ActionStepCard 
                step={step} 
                onStatusChange={(id, newStatus) => handleStatusChange(id, newStatus)}
              />
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
