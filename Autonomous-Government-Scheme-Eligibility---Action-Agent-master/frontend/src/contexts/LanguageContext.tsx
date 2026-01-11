import { createContext, useContext, useState, ReactNode } from 'react';

export type Language = 'en' | 'hi';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Navigation
    'nav.home': 'Home',
    'nav.profile': 'Profile',
    'nav.schemes': 'Schemes',
    'nav.actionPlan': 'Action Plan',
    'nav.reminders': 'Reminders',
    'nav.getStarted': 'Get Started',
    
    // Landing Page
    'landing.badge': 'Your Digital Government Case Worker',
    'landing.hero.title1': 'Discover Government',
    'landing.hero.title2': 'Benefits You Deserve',
    'landing.hero.subtitle': 'Stop missing out on life-changing benefits. We match your profile with',
    'landing.hero.schemes': '1000+ schemes',
    'landing.hero.subtitleEnd': 'and guide you every step of the way.',
    'landing.cta.start': 'Start Free Check',
    'landing.cta.explore': 'Explore Schemes',
    'landing.trust.free': '100% Free',
    'landing.trust.noReg': 'No Registration Required',
    'landing.trust.instant': 'Instant Results',
    
    // Stats
    'stats.schemes': 'Schemes',
    'stats.citizens': 'Citizens',
    'stats.benefits': 'Benefits',
    'stats.states': 'States',
    
    // Problem Section
    'problem.label': 'The Challenge',
    'problem.title': 'Why Millions Miss Out',
    'problem.subtitle': 'Every year, crores of eligible citizens fail to access benefits that could transform their lives.',
    'problem.complex.title': 'Complex Rules',
    'problem.complex.desc': 'Eligibility criteria are scattered across multiple portals and difficult to understand.',
    'problem.middlemen.title': 'Middlemen',
    'problem.middlemen.desc': 'Dependency on agents leads to corruption, delays, and incomplete applications.',
    'problem.awareness.title': 'Low Awareness',
    'problem.awareness.desc': 'Most eligible citizens never learn about schemes that could transform their lives.',
    
    // Features Section
    'features.label': 'Our Solution',
    'features.title': 'Your Personal Case Worker',
    'features.subtitle': 'We\'ve automated the entire eligibility discovery process so you can focus on what matters.',
    'features.discovery.title': 'Smart Discovery',
    'features.discovery.desc': 'AI-powered matching from 1000+ government schemes tailored to your profile.',
    'features.eligibility.title': 'Instant Eligibility',
    'features.eligibility.desc': 'Get clear, transparent decisions with detailed reasoning for each scheme.',
    'features.documents.title': 'Document Tracker',
    'features.documents.desc': 'Know exactly what documents you need with real-time progress tracking.',
    'features.actions.title': 'Action Plans',
    'features.actions.desc': 'Step-by-step guidance with smart reminders to never miss a deadline.',
    
    // How It Works
    'howItWorks.label': 'How It Works',
    'howItWorks.title': '4 Simple Steps',
    'howItWorks.step1.title': 'Create Profile',
    'howItWorks.step1.desc': 'Share basic details about yourself',
    'howItWorks.step2.title': 'Discover Schemes',
    'howItWorks.step2.desc': 'See matched government schemes',
    'howItWorks.step3.title': 'Check Documents',
    'howItWorks.step3.desc': 'Know what papers you need',
    'howItWorks.step4.title': 'Take Action',
    'howItWorks.step4.desc': 'Follow your personalized plan',
    
    // CTA Section
    'cta.title': 'Ready to Claim Your Benefits?',
    'cta.subtitle': 'Join lakhs of citizens who have discovered schemes they\'re eligible for. It takes just 2 minutes to get started — completely free.',
    'cta.button': 'Start Your Free Check',
    
    // Profile Page
    'profile.title': 'Build Your Profile',
    'profile.titleComplete': 'Your Profile',
    'profile.subtitle': 'Help us understand your background to find the best schemes for you.',
    'profile.subtitleComplete': 'Review your information before proceeding to scheme discovery.',
    'profile.step.personal': 'Personal Details',
    'profile.step.location': 'Location & Income',
    'profile.step.occupation': 'Occupation & Status',
    'profile.age': 'Age',
    'profile.gender': 'Gender',
    'profile.gender.male': 'Male',
    'profile.gender.female': 'Female',
    'profile.gender.other': 'Other',
    'profile.category': 'Category',
    'profile.disability': 'Person with Disability',
    'profile.disability.desc': 'Select if applicable for special schemes',
    'profile.state': 'State',
    'profile.income': 'Annual Family Income',
    'profile.occupation': 'Occupation',
    'profile.education': 'Education Level',
    'profile.familyStatus': 'Family Status',
    'profile.back': 'Back',
    'profile.next': 'Next Step',
    'profile.complete': 'Complete Profile',
    'profile.edit': 'Edit Profile',
    'profile.proceed': 'Proceed to Scheme Discovery',
    
    // Schemes Page
    'schemes.title': 'Scheme Discovery Dashboard',
    'schemes.subtitle': 'Based on your profile, we\'ve analyzed {count} government schemes for your eligibility.',
    'schemes.eligible': 'Eligible',
    'schemes.conditional': 'Conditional',
    'schemes.notEligible': 'Not Eligible',
    'schemes.search': 'Search schemes...',
    'schemes.status': 'Status:',
    'schemes.all': 'All',
    'schemes.noResults': 'No schemes found matching your criteria.',
    'schemes.viewDetails': 'View Details',
    'schemes.relevance': 'Match',
    
    // Action Plan Page
    'actionPlan.title': 'Your Action Plan',
    'actionPlan.subtitle': 'Follow these steps to apply for your eligible schemes. Complete tasks in order for best results.',
    'actionPlan.progress': 'Overall Progress',
    'actionPlan.completed': 'Completed',
    'actionPlan.inProgress': 'In Progress',
    'actionPlan.pending': 'Pending',
    'actionPlan.stepsCompleted': '{completed} of {total} steps completed',
    'actionPlan.markComplete': 'Mark Complete',
    'actionPlan.startTask': 'Start Task',
    
    // Reminders Page
    'reminders.title': 'Follow-up & Reminders',
    'reminders.subtitle': 'Stay on track with your scheme applications and deadlines.',
    'reminders.sync': 'Sync Updates',
    'reminders.upcoming': 'Upcoming',
    'reminders.overdue': 'Overdue',
    'reminders.total': 'Total',
    'reminders.profileUpdate': 'Keep Your Profile Updated',
    'reminders.profileUpdateDesc': 'Changes in your income, occupation, or family status may unlock new schemes. Update your profile regularly for best results.',
    'reminders.updateProfile': 'Update Profile',
    'reminders.allCaughtUp': 'All caught up!',
    'reminders.noPending': 'You have no pending reminders at the moment.',
    'reminders.noCompleted': 'No completed reminders yet',
    'reminders.completeToSee': 'Complete some pending reminders to see them here.',
    'reminders.markDone': 'Mark Done',
    
    // Footer
    'footer.tagline': 'Making government schemes accessible to all',
    'footer.builtWith': 'Built with',
    'footer.forCitizens': 'for citizens',
    'footer.rights': '© 2025 GovScheme. All rights reserved.',
    'footer.privacy': 'Privacy Policy',
    'footer.terms': 'Terms of Service',
    'footer.help': 'Help Center',
    
    // Accessibility
    'accessibility.language': 'Language',
    'accessibility.fontSize': 'Font Size',
    'accessibility.increase': 'Increase',
    'accessibility.decrease': 'Decrease',
    'accessibility.reset': 'Reset',
    
    // Auth
    'auth.login.title': 'Welcome Back',
    'auth.login.subtitle': 'Sign in to access your personalized schemes',
    'auth.login.button': 'Sign In',
    'auth.login.noAccount': "Don't have an account?",
    'auth.login.registerLink': 'Register here',
    'auth.register.title': 'Create Account',
    'auth.register.subtitle': 'Join to discover schemes tailored for you',
    'auth.register.button': 'Create Account',
    'auth.register.hasAccount': 'Already have an account?',
    'auth.register.loginLink': 'Sign in',
    'auth.email': 'Email',
    'auth.password': 'Password',
    'auth.confirmPassword': 'Confirm Password',
    'auth.name': 'Full Name',
    'auth.role': 'I am a',
    'auth.roles.student': 'Student',
    'auth.roles.farmer': 'Farmer',
    'auth.logout': 'Logout',
  },
  hi: {
    // Navigation
    'nav.home': 'होम',
    'nav.profile': 'प्रोफ़ाइल',
    'nav.schemes': 'योजनाएं',
    'nav.actionPlan': 'कार्य योजना',
    'nav.reminders': 'रिमाइंडर',
    'nav.getStarted': 'शुरू करें',
    
    // Landing Page
    'landing.badge': 'आपका डिजिटल सरकारी केस वर्कर',
    'landing.hero.title1': 'सरकारी लाभ खोजें',
    'landing.hero.title2': 'जो आपके हक़ में हैं',
    'landing.hero.subtitle': 'जीवन बदलने वाले लाभों से न चूकें। हम आपकी प्रोफ़ाइल को',
    'landing.hero.schemes': '1000+ योजनाओं',
    'landing.hero.subtitleEnd': 'से मिलान करते हैं और हर कदम पर आपका मार्गदर्शन करते हैं।',
    'landing.cta.start': 'मुफ्त जांच शुरू करें',
    'landing.cta.explore': 'योजनाएं देखें',
    'landing.trust.free': '100% मुफ्त',
    'landing.trust.noReg': 'पंजीकरण आवश्यक नहीं',
    'landing.trust.instant': 'तुरंत परिणाम',
    
    // Stats
    'stats.schemes': 'योजनाएं',
    'stats.citizens': 'नागरिक',
    'stats.benefits': 'लाभ',
    'stats.states': 'राज्य',
    
    // Problem Section
    'problem.label': 'चुनौती',
    'problem.title': 'लाखों लोग क्यों चूक जाते हैं',
    'problem.subtitle': 'हर साल, करोड़ों पात्र नागरिक उन लाभों तक नहीं पहुंच पाते जो उनका जीवन बदल सकते हैं।',
    'problem.complex.title': 'जटिल नियम',
    'problem.complex.desc': 'पात्रता मानदंड कई पोर्टलों पर बिखरे हुए हैं और समझने में कठिन हैं।',
    'problem.middlemen.title': 'बिचौलिए',
    'problem.middlemen.desc': 'एजेंटों पर निर्भरता से भ्रष्टाचार, देरी और अधूरे आवेदन होते हैं।',
    'problem.awareness.title': 'कम जागरूकता',
    'problem.awareness.desc': 'अधिकांश पात्र नागरिक उन योजनाओं के बारे में कभी नहीं जान पाते।',
    
    // Features Section
    'features.label': 'हमारा समाधान',
    'features.title': 'आपका व्यक्तिगत केस वर्कर',
    'features.subtitle': 'हमने पूरी पात्रता खोज प्रक्रिया को स्वचालित कर दिया है।',
    'features.discovery.title': 'स्मार्ट खोज',
    'features.discovery.desc': '1000+ सरकारी योजनाओं से AI-संचालित मिलान।',
    'features.eligibility.title': 'तुरंत पात्रता',
    'features.eligibility.desc': 'विस्तृत कारणों के साथ स्पष्ट निर्णय प्राप्त करें।',
    'features.documents.title': 'दस्तावेज़ ट्रैकर',
    'features.documents.desc': 'जानें कि आपको कौन से दस्तावेज़ चाहिए।',
    'features.actions.title': 'कार्य योजनाएं',
    'features.actions.desc': 'स्मार्ट रिमाइंडर के साथ चरण-दर-चरण मार्गदर्शन।',
    
    // How It Works
    'howItWorks.label': 'कैसे काम करता है',
    'howItWorks.title': '4 सरल चरण',
    'howItWorks.step1.title': 'प्रोफ़ाइल बनाएं',
    'howItWorks.step1.desc': 'अपने बारे में बुनियादी जानकारी साझा करें',
    'howItWorks.step2.title': 'योजनाएं खोजें',
    'howItWorks.step2.desc': 'मिलान की गई सरकारी योजनाएं देखें',
    'howItWorks.step3.title': 'दस्तावेज़ जांचें',
    'howItWorks.step3.desc': 'जानें कौन से कागज़ात चाहिए',
    'howItWorks.step4.title': 'कार्रवाई करें',
    'howItWorks.step4.desc': 'अपनी व्यक्तिगत योजना का पालन करें',
    
    // CTA Section
    'cta.title': 'अपने लाभ पाने के लिए तैयार हैं?',
    'cta.subtitle': 'उन लाखों नागरिकों से जुड़ें जिन्होंने अपनी पात्र योजनाएं खोजी हैं। शुरू करने में सिर्फ 2 मिनट लगते हैं — पूरी तरह मुफ्त।',
    'cta.button': 'मुफ्त जांच शुरू करें',
    
    // Profile Page
    'profile.title': 'अपनी प्रोफ़ाइल बनाएं',
    'profile.titleComplete': 'आपकी प्रोफ़ाइल',
    'profile.subtitle': 'आपके लिए सर्वोत्तम योजनाएं खोजने में हमारी मदद करें।',
    'profile.subtitleComplete': 'योजना खोज पर जाने से पहले अपनी जानकारी की समीक्षा करें।',
    'profile.step.personal': 'व्यक्तिगत विवरण',
    'profile.step.location': 'स्थान और आय',
    'profile.step.occupation': 'व्यवसाय और स्थिति',
    'profile.age': 'आयु',
    'profile.gender': 'लिंग',
    'profile.gender.male': 'पुरुष',
    'profile.gender.female': 'महिला',
    'profile.gender.other': 'अन्य',
    'profile.category': 'श्रेणी',
    'profile.disability': 'दिव्यांग व्यक्ति',
    'profile.disability.desc': 'विशेष योजनाओं के लिए लागू होने पर चुनें',
    'profile.state': 'राज्य',
    'profile.income': 'वार्षिक पारिवारिक आय',
    'profile.occupation': 'व्यवसाय',
    'profile.education': 'शिक्षा स्तर',
    'profile.familyStatus': 'पारिवारिक स्थिति',
    'profile.back': 'पीछे',
    'profile.next': 'अगला चरण',
    'profile.complete': 'प्रोफ़ाइल पूरी करें',
    'profile.edit': 'प्रोफ़ाइल संपादित करें',
    'profile.proceed': 'योजना खोज पर जाएं',
    
    // Schemes Page
    'schemes.title': 'योजना खोज डैशबोर्ड',
    'schemes.subtitle': 'आपकी प्रोफ़ाइल के आधार पर, हमने {count} सरकारी योजनाओं का विश्लेषण किया है।',
    'schemes.eligible': 'पात्र',
    'schemes.conditional': 'सशर्त',
    'schemes.notEligible': 'पात्र नहीं',
    'schemes.search': 'योजनाएं खोजें...',
    'schemes.status': 'स्थिति:',
    'schemes.all': 'सभी',
    'schemes.noResults': 'आपके मानदंडों से मेल खाती कोई योजना नहीं मिली।',
    'schemes.viewDetails': 'विवरण देखें',
    'schemes.relevance': 'मिलान',
    
    // Action Plan Page
    'actionPlan.title': 'आपकी कार्य योजना',
    'actionPlan.subtitle': 'अपनी पात्र योजनाओं के लिए आवेदन करने के लिए इन चरणों का पालन करें।',
    'actionPlan.progress': 'समग्र प्रगति',
    'actionPlan.completed': 'पूर्ण',
    'actionPlan.inProgress': 'प्रगति में',
    'actionPlan.pending': 'लंबित',
    'actionPlan.stepsCompleted': '{total} में से {completed} चरण पूर्ण',
    'actionPlan.markComplete': 'पूर्ण चिह्नित करें',
    'actionPlan.startTask': 'कार्य शुरू करें',
    
    // Reminders Page
    'reminders.title': 'फॉलो-अप और रिमाइंडर',
    'reminders.subtitle': 'अपने योजना आवेदनों और समय-सीमाओं पर नज़र रखें।',
    'reminders.sync': 'अपडेट सिंक करें',
    'reminders.upcoming': 'आगामी',
    'reminders.overdue': 'विलंबित',
    'reminders.total': 'कुल',
    'reminders.profileUpdate': 'अपनी प्रोफ़ाइल अपडेट रखें',
    'reminders.profileUpdateDesc': 'आय, व्यवसाय या पारिवारिक स्थिति में बदलाव से नई योजनाएं खुल सकती हैं।',
    'reminders.updateProfile': 'प्रोफ़ाइल अपडेट करें',
    'reminders.allCaughtUp': 'सब अपडेट है!',
    'reminders.noPending': 'इस समय कोई लंबित रिमाइंडर नहीं है।',
    'reminders.noCompleted': 'अभी तक कोई पूर्ण रिमाइंडर नहीं',
    'reminders.completeToSee': 'यहां देखने के लिए कुछ रिमाइंडर पूर्ण करें।',
    'reminders.markDone': 'पूर्ण करें',
    
    // Footer
    'footer.tagline': 'सरकारी योजनाओं को सभी के लिए सुलभ बनाना',
    'footer.builtWith': 'नागरिकों के लिए',
    'footer.forCitizens': 'प्यार से बनाया',
    'footer.rights': '© 2025 GovScheme. सर्वाधिकार सुरक्षित।',
    'footer.privacy': 'गोपनीयता नीति',
    'footer.terms': 'सेवा की शर्तें',
    'footer.help': 'सहायता केंद्र',
    
    // Accessibility
    'accessibility.language': 'भाषा',
    'accessibility.fontSize': 'फ़ॉन्ट आकार',
    'accessibility.increase': 'बढ़ाएं',
    'accessibility.decrease': 'घटाएं',
    'accessibility.reset': 'रीसेट',
    
    // Auth
    'auth.login.title': 'वापसी पर स्वागत है',
    'auth.login.subtitle': 'अपनी व्यक्तिगत योजनाओं तक पहुंचने के लिए साइन इन करें',
    'auth.login.button': 'साइन इन करें',
    'auth.login.noAccount': 'खाता नहीं है?',
    'auth.login.registerLink': 'यहां पंजीकरण करें',
    'auth.register.title': 'खाता बनाएं',
    'auth.register.subtitle': 'आपके लिए अनुकूलित योजनाएं खोजने के लिए जुड़ें',
    'auth.register.button': 'खाता बनाएं',
    'auth.register.hasAccount': 'पहले से खाता है?',
    'auth.register.loginLink': 'साइन इन करें',
    'auth.email': 'ईमेल',
    'auth.password': 'पासवर्ड',
    'auth.confirmPassword': 'पासवर्ड की पुष्टि करें',
    'auth.name': 'पूरा नाम',
    'auth.role': 'मैं हूं',
    'auth.roles.student': 'छात्र',
    'auth.roles.farmer': 'किसान',
    'auth.logout': 'लॉग आउट',
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
