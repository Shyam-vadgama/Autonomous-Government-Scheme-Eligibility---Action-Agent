import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ReminderCard } from '@/components/reminders/ReminderCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { mockReminders, Reminder } from '@/lib/mockData';
import { useLanguage } from '@/contexts/LanguageContext';
import { Bell, Calendar, CheckCircle2, RefreshCw, AlertCircle, User } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function DashboardReminders() {
  const { t } = useLanguage();
  const [reminders, setReminders] = useState<Reminder[]>(mockReminders);

  const pendingReminders = reminders.filter(r => r.status === 'pending');
  const completedReminders = reminders.filter(r => r.status === 'completed');

  const today = new Date();
  const upcomingCount = pendingReminders.filter(r => new Date(r.date) >= today).length;
  const overdueCount = pendingReminders.filter(r => new Date(r.date) < today).length;

  const handleMarkComplete = (id: string) => {
    setReminders(prev => prev.map(r => 
      r.id === id ? { ...r, status: 'completed' as const } : r
    ));
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-6 md:py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground mb-2">
              {t('reminders.title')}
            </h1>
            <p className="text-muted-foreground">
              {t('reminders.subtitle')}
            </p>
          </div>
          <Button variant="outline" className="gap-2 w-fit">
            <RefreshCw className="h-4 w-4" />
            {t('reminders.sync')}
          </Button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-3 md:gap-4 mb-6">
          <div className="bg-primary/10 border border-primary/20 rounded-xl p-3 md:p-4 flex items-center gap-2 md:gap-3">
            <Calendar className="h-6 w-6 md:h-8 md:w-8 text-primary" />
            <div>
              <p className="text-xl md:text-2xl font-bold text-foreground">{upcomingCount}</p>
              <p className="text-xs md:text-sm text-muted-foreground">{t('reminders.upcoming')}</p>
            </div>
          </div>
          <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-3 md:p-4 flex items-center gap-2 md:gap-3">
            <AlertCircle className="h-6 w-6 md:h-8 md:w-8 text-destructive" />
            <div>
              <p className="text-xl md:text-2xl font-bold text-foreground">{overdueCount}</p>
              <p className="text-xs md:text-sm text-muted-foreground">{t('reminders.overdue')}</p>
            </div>
          </div>
          <div className="bg-muted border border-border rounded-xl p-3 md:p-4 flex items-center gap-2 md:gap-3">
            <Bell className="h-6 w-6 md:h-8 md:w-8 text-muted-foreground" />
            <div>
              <p className="text-xl md:text-2xl font-bold text-foreground">{reminders.length}</p>
              <p className="text-xs md:text-sm text-muted-foreground">{t('reminders.total')}</p>
            </div>
          </div>
        </div>

        {/* Profile Update Card */}
        <Card className="mb-6 border-primary/20 bg-primary/5">
          <CardContent className="p-4 md:p-6">
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 shrink-0">
                <User className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-foreground mb-1">{t('reminders.profileUpdate')}</h3>
                <p className="text-sm text-muted-foreground">{t('reminders.profileUpdateDesc')}</p>
              </div>
              <Link to="/dashboard/profile">
                <Button variant="outline" className="w-full md:w-auto">
                  {t('reminders.updateProfile')}
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Reminders Tabs */}
        <Tabs defaultValue="pending" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
            <TabsTrigger value="pending" className="gap-2">
              <Bell className="h-4 w-4" />
              Pending ({pendingReminders.length})
            </TabsTrigger>
            <TabsTrigger value="completed" className="gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Completed ({completedReminders.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="space-y-4">
            {pendingReminders.length > 0 ? (
              pendingReminders.map((reminder, index) => (
                <div key={reminder.id} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                  <ReminderCard 
                    reminder={reminder} 
                    onComplete={() => handleMarkComplete(reminder.id)}
                  />
                </div>
              ))
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <CheckCircle2 className="h-12 w-12 text-success mx-auto mb-4" />
                  <h3 className="font-medium text-foreground mb-2">{t('reminders.allCaughtUp')}</h3>
                  <p className="text-sm text-muted-foreground">{t('reminders.noPending')}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="completed" className="space-y-4">
            {completedReminders.length > 0 ? (
              completedReminders.map((reminder, index) => (
                <div key={reminder.id} className="animate-fade-in opacity-70" style={{ animationDelay: `${index * 100}ms` }}>
                  <ReminderCard 
                    reminder={reminder} 
                    onComplete={() => {}}
                  />
                </div>
              ))
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="font-medium text-foreground mb-2">{t('reminders.noCompleted')}</h3>
                  <p className="text-sm text-muted-foreground">{t('reminders.completeToSee')}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
