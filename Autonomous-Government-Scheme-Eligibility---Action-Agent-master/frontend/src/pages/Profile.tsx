import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { ProfileForm } from '@/components/profile/ProfileForm';
import { ProfileSummary } from '@/components/profile/ProfileSummary';
import { useProfile } from '@/contexts/ProfileContext';
import { useLanguage } from '@/contexts/LanguageContext';

export default function Profile() {
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
    navigate('/schemes');
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-2">
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
    </Layout>
  );
}
