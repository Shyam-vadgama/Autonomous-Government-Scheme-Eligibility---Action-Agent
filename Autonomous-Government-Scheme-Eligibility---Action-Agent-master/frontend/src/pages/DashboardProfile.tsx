import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ProfileForm } from '@/components/profile/ProfileForm';
import { ProfileSummary } from '@/components/profile/ProfileSummary';
import { useProfile } from '@/contexts/ProfileContext';
import { useLanguage } from '@/contexts/LanguageContext';

export default function DashboardProfile() {
  const navigate = useNavigate();
  const { setCurrentStep } = useProfile();
  const { t } = useLanguage();
  const [showSummary, setShowSummary] = useState(false);

  const handleFormComplete = () => {
    setShowSummary(true);
  };

  const handleEdit = () => {
    setCurrentStep(0);
    setShowSummary(false);
  };

  const handleProceed = () => {
    navigate('/dashboard/schemes');
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-6 md:py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground mb-2">
              {showSummary ? t('profile.titleComplete') : t('profile.title')}
            </h1>
            <p className="text-muted-foreground">
              {showSummary ? t('profile.subtitleComplete') : t('profile.subtitle')}
            </p>
          </div>

          {showSummary ? (
            <ProfileSummary onEdit={handleEdit} onProceed={handleProceed} />
          ) : (
            <ProfileForm onComplete={handleFormComplete} />
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
