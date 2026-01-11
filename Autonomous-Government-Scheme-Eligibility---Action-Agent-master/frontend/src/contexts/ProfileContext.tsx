import React, { createContext, useContext, useState, ReactNode } from 'react';
import { CitizenProfile, defaultProfile } from '@/lib/mockData';

interface ProfileContextType {
  profile: CitizenProfile;
  setProfile: (profile: CitizenProfile) => void;
  updateProfile: (updates: Partial<CitizenProfile>) => void;
  isProfileComplete: boolean;
  currentStep: number;
  setCurrentStep: (step: number) => void;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<CitizenProfile>({
    ...defaultProfile,
    documents: defaultProfile.documents || {}
  });
  const [currentStep, setCurrentStep] = useState(0);

  const updateProfile = (updates: Partial<CitizenProfile>) => {
    setProfile(prev => {
      const newProfile = { ...prev, ...updates };
      // Ensure documents object is preserved and merged if updates contain documents
      if (updates.documents) {
        newProfile.documents = { ...(prev.documents || {}), ...updates.documents };
      } else if (!newProfile.documents) {
        newProfile.documents = prev.documents || {};
      }
      return newProfile;
    });
  };

  const isProfileComplete = Boolean(
    profile.fullName &&
    profile.age &&
    profile.gender &&
    profile.dob &&
    profile.mobileNumber &&
    profile.email &&
    profile.address &&
    profile.state &&
    profile.district &&
    profile.pincode &&
    profile.incomeRange &&
    profile.occupation &&
    profile.category &&
    profile.education &&
    profile.familyStatus &&
    profile.aadhaarNumber &&
    profile.bankAccountNumber &&
    profile.ifscCode &&
    // Conditional checks
    (profile.occupation === 'Student' ? (profile.currentCourse && profile.institution) : true) &&
    (profile.occupation === 'Farmer' ? (profile.landHolding && profile.farmingType) : true) &&
    // Document checks (simulate file presence) - safely accessed
    profile.documents?.aadhaarCard &&
    profile.documents?.panCard &&
    profile.documents?.incomeCertificate &&
    profile.documents?.casteCertificate &&
    profile.documents?.markSheet
  );

  return (
    <ProfileContext.Provider value={{
      profile,
      setProfile,
      updateProfile,
      isProfileComplete,
      currentStep,
      setCurrentStep
    }}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  const context = useContext(ProfileContext);
  if (context === undefined) {
    throw new Error('useProfile must be used within a ProfileProvider');
  }
  return context;
}
