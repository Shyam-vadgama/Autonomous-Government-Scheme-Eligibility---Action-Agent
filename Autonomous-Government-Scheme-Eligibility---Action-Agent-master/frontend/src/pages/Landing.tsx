import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Shield, 
  Search, 
  FileCheck, 
  ClipboardList, 
  ArrowRight,
  Users,
  FileX,
  Clock,
  CheckCircle2,
  Sparkles,
  Zap,
  TrendingUp
} from 'lucide-react';

export default function Landing() {
  const { t } = useLanguage();

  const features = [
    {
      icon: Search,
      titleKey: 'features.discovery.title',
      descKey: 'features.discovery.desc',
      color: 'bg-blue-500',
    },
    {
      icon: FileCheck,
      titleKey: 'features.eligibility.title',
      descKey: 'features.eligibility.desc',
      color: 'bg-emerald-500',
    },
    {
      icon: ClipboardList,
      titleKey: 'features.documents.title',
      descKey: 'features.documents.desc',
      color: 'bg-amber-500',
    },
    {
      icon: Clock,
      titleKey: 'features.actions.title',
      descKey: 'features.actions.desc',
      color: 'bg-purple-500',
    },
  ];

  const problems = [
    {
      icon: FileX,
      titleKey: 'problem.complex.title',
      descKey: 'problem.complex.desc',
    },
    {
      icon: Users,
      titleKey: 'problem.middlemen.title',
      descKey: 'problem.middlemen.desc',
    },
    {
      icon: Search,
      titleKey: 'problem.awareness.title',
      descKey: 'problem.awareness.desc',
    },
  ];

  const stats = [
    { value: '1000+', labelKey: 'stats.schemes', icon: FileCheck },
    { value: '10L+', labelKey: 'stats.citizens', icon: Users },
    { value: '₹500Cr+', labelKey: 'stats.benefits', icon: TrendingUp },
    { value: '29', labelKey: 'stats.states', icon: Shield },
  ];

  const steps = [
    { step: '1', titleKey: 'howItWorks.step1.title', descKey: 'howItWorks.step1.desc', icon: Users },
    { step: '2', titleKey: 'howItWorks.step2.title', descKey: 'howItWorks.step2.desc', icon: Search },
    { step: '3', titleKey: 'howItWorks.step3.title', descKey: 'howItWorks.step3.desc', icon: FileCheck },
    { step: '4', titleKey: 'howItWorks.step4.title', descKey: 'howItWorks.step4.desc', icon: ClipboardList },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative gradient-hero min-h-[80vh] flex items-center">
        <div className="container mx-auto px-4 py-16 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-white/15 px-4 py-2 rounded-full mb-6 border border-white/20">
              <Sparkles className="h-4 w-4 text-secondary" />
              <span className="text-sm font-medium text-white">{t('landing.badge')}</span>
            </div>
            
            {/* Heading */}
            <h1 className="font-display text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
              {t('landing.hero.title1')}
              <span className="block mt-2 text-secondary">
                {t('landing.hero.title2')}
              </span>
            </h1>
            
            {/* Subheading */}
            <p className="text-lg md:text-xl text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed">
              {t('landing.hero.subtitle')}
              <span className="font-semibold text-white"> {t('landing.hero.schemes')} </span> 
              {t('landing.hero.subtitleEnd')}
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/profile">
                <Button variant="secondary" size="lg" className="gap-2 px-8">
                  {t('landing.cta.start')}
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link to="/schemes">
                <Button 
                  variant="outline" 
                  size="lg" 
                  className="border-2 border-white bg-white/10 text-white hover:bg-white hover:text-primary font-medium"
                >
                  {t('landing.cta.explore')}
                </Button>
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center justify-center gap-6 mt-10 flex-wrap">
              <div className="flex items-center gap-2 text-white/90">
                <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                <span className="text-sm">{t('landing.trust.free')}</span>
              </div>
              <div className="flex items-center gap-2 text-white/90">
                <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                <span className="text-sm">{t('landing.trust.noReg')}</span>
              </div>
              <div className="flex items-center gap-2 text-white/90">
                <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                <span className="text-sm">{t('landing.trust.instant')}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {stats.map((stat) => {
              const Icon = stat.icon;
              return (
                <Card key={stat.labelKey} className="bg-card border-border">
                  <CardContent className="p-6 flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl gradient-hero shrink-0">
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="font-display text-2xl md:text-3xl font-bold text-foreground">
                        {stat.value}
                      </p>
                      <p className="text-sm text-muted-foreground">{t(stat.labelKey)}</p>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-flex items-center gap-2 text-destructive font-semibold text-sm uppercase tracking-wider mb-3">
              <Zap className="h-4 w-4" />
              {t('problem.label')}
            </span>
            <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
              {t('problem.title')}
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('problem.subtitle')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {problems.map((problem) => {
              const Icon = problem.icon;
              return (
                <Card key={problem.titleKey} className="border-destructive/20 bg-card hover:border-destructive/40 transition-colors">
                  <CardContent className="p-6">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-destructive/10 mb-4">
                      <Icon className="h-6 w-6 text-destructive" />
                    </div>
                    <h3 className="font-display text-lg font-bold text-foreground mb-2">
                      {t(problem.titleKey)}
                    </h3>
                    <p className="text-muted-foreground">{t(problem.descKey)}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-flex items-center gap-2 text-primary font-semibold text-sm uppercase tracking-wider mb-3">
              <Sparkles className="h-4 w-4" />
              {t('features.label')}
            </span>
            <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
              {t('features.title')}
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('features.subtitle')}
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <Card key={feature.titleKey} className="bg-card border-border hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${feature.color} mb-4`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-display text-lg font-bold text-foreground mb-2">
                      {t(feature.titleKey)}
                    </h3>
                    <p className="text-muted-foreground">{t(feature.descKey)}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <span className="inline-flex items-center gap-2 text-primary font-semibold text-sm uppercase tracking-wider mb-3">
              <Zap className="h-4 w-4" />
              {t('howItWorks.label')}
            </span>
            <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
              {t('howItWorks.title')}
            </h2>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {steps.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.step} className="text-center">
                  <div className="relative inline-block mb-4">
                    <div className="flex h-16 w-16 items-center justify-center rounded-xl gradient-hero mx-auto">
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 flex h-7 w-7 items-center justify-center rounded-full bg-secondary text-secondary-foreground font-bold text-sm">
                      {item.step}
                    </div>
                  </div>
                  <h3 className="font-display text-lg font-bold text-foreground mb-2">{t(item.titleKey)}</h3>
                  <p className="text-sm text-muted-foreground">{t(item.descKey)}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-background">
        <div className="container mx-auto px-4">
          <Card className="overflow-hidden border-0">
            <div className="gradient-hero">
              <CardContent className="p-10 md:p-14 text-center">
                <div className="inline-flex h-16 w-16 items-center justify-center rounded-xl bg-white/15 mb-6 border border-white/20">
                  <CheckCircle2 className="h-8 w-8 text-white" />
                </div>
                <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
                  {t('cta.title')}
                </h2>
                <p className="text-white/90 text-lg max-w-xl mx-auto mb-8">
                  {t('cta.subtitle')}
                </p>
                <Link to="/profile">
                  <Button variant="secondary" size="lg" className="gap-2 px-8">
                    {t('cta.button')}
                    <ArrowRight className="h-5 w-5" />
                  </Button>
                </Link>
              </CardContent>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
