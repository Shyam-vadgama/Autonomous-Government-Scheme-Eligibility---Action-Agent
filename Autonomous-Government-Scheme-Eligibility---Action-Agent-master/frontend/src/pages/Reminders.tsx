import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { ReminderCard } from '@/components/reminders/ReminderCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { mockReminders, Reminder } from '@/lib/mockData';
import { Bell, CheckCircle2, Clock, RefreshCw, AlertTriangle, Sparkles } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

export default function Reminders() {
  const [reminders, setReminders] = useState<Reminder[]>(mockReminders);
  const [showCompleted, setShowCompleted] = useState(false);

  const handleComplete = (id: string) => {
    setReminders(prev => prev.map(r => 
      r.id === id ? { ...r, status: 'completed' as const } : r
    ));
    toast({
      title: "Reminder completed!",
      description: "Great job staying on track with your applications.",
    });
  };

  const handleRefresh = () => {
    toast({
      title: "Profile synced!",
      description: "Your reminders have been updated based on latest scheme deadlines.",
    });
  };

  const pendingReminders = reminders.filter(r => r.status === 'pending');
  const completedReminders = reminders.filter(r => r.status === 'completed');
  const displayedReminders = showCompleted ? completedReminders : pendingReminders;

  const upcomingCount = pendingReminders.length;
  const overdueCount = pendingReminders.filter(r => {
    const date = new Date(r.date);
    return date < new Date();
  }).length;

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-2">
              Follow-up & Reminders
            </h1>
            <p className="text-muted-foreground">
              Stay on track with your scheme applications and deadlines.
            </p>
          </div>
          <Button variant="outline" onClick={handleRefresh} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Sync Updates
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="shadow-card">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-info/10">
                <Bell className="h-5 w-5 text-info" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{upcomingCount}</p>
                <p className="text-xs text-muted-foreground">Upcoming</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-card">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-destructive/10">
                <AlertTriangle className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{overdueCount}</p>
                <p className="text-xs text-muted-foreground">Overdue</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-card">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10">
                <CheckCircle2 className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{completedReminders.length}</p>
                <p className="text-xs text-muted-foreground">Completed</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-card">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Clock className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold text-foreground">{reminders.length}</p>
                <p className="text-xs text-muted-foreground">Total</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Profile Update Notice */}
        <Card className="mb-8 border-primary/20 bg-primary/5">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full gradient-hero shrink-0">
              <Sparkles className="h-6 w-6 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-foreground">Keep Your Profile Updated</h3>
              <p className="text-sm text-muted-foreground">
                Changes in your income, occupation, or family status may unlock new schemes. 
                Update your profile regularly for best results.
              </p>
            </div>
            <Button variant="outline" size="sm">
              Update Profile
            </Button>
          </CardContent>
        </Card>

        {/* Toggle */}
        <div className="flex items-center gap-2 mb-6">
          <Button
            variant={!showCompleted ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowCompleted(false)}
          >
            Pending ({pendingReminders.length})
          </Button>
          <Button
            variant={showCompleted ? 'default' : 'outline'}
            size="sm"
            onClick={() => setShowCompleted(true)}
          >
            Completed ({completedReminders.length})
          </Button>
        </div>

        {/* Reminders List */}
        <div className="space-y-4">
          {displayedReminders.length > 0 ? (
            displayedReminders.map((reminder, index) => (
              <div key={reminder.id} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <ReminderCard reminder={reminder} onComplete={handleComplete} />
              </div>
            ))
          ) : (
            <Card className="shadow-card">
              <CardContent className="p-8 text-center">
                <CheckCircle2 className="h-12 w-12 text-success mx-auto mb-4" />
                <h3 className="font-semibold text-foreground mb-1">
                  {showCompleted ? 'No completed reminders yet' : 'All caught up!'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {showCompleted 
                    ? 'Complete some pending reminders to see them here.' 
                    : 'You have no pending reminders at the moment.'}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
}
