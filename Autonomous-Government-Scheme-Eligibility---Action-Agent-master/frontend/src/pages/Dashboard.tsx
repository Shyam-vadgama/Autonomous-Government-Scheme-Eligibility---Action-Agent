import { Link } from 'react-router-dom';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useProfile } from '@/contexts/ProfileContext';
import { getSchemesByRole, mockActionSteps, mockReminders, Scheme } from '@/lib/mockData';
import { api } from '@/lib/api';
import { 
  FileText, 
  ClipboardList, 
  Bell, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight,
  GraduationCap,
  Wheat,
  User,
  Loader2,
  Edit2
} from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const { profile } = useProfile();
  
  const userRole = user?.role || 'student';
  
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSchemes = async () => {
      setIsLoading(true);
      try {
        const apiSchemes = await api.schemes.getAll();
        
        if (apiSchemes && apiSchemes.length > 0) {
          const mappedSchemes: Scheme[] = apiSchemes.map((s: any, index) => ({
            id: s.scheme_id || `api-${index}`,
            name: s.name || s.title,
            category: s.category || 'General',
            targetGroup: (s.target_groups && s.target_groups.includes('student')) ? 'student' : 
                         (s.target_groups && s.target_groups.includes('farmer')) ? 'farmer' : 'both',
            description: s.description || s.snippet || '',
            benefits: s.benefits || 'View details for benefits',
            relevanceScore: s.relevance_score ? Math.round(s.relevance_score * 100) : 0,
            status: (s.status === 'eligible' || s.status === 'conditional' || s.status === 'rejected') ? s.status : 'eligible',
            reason: s.reason || 'Available scheme',
            requiredDocuments: [] 
          }));
          
          // Filter by role
          const filtered = mappedSchemes.filter(s => 
             s.targetGroup === userRole || s.targetGroup === 'both'
          );
          setSchemes(filtered);
        } else {
          setSchemes(getSchemesByRole(userRole));
        }
      } catch (error) {
        console.error("Failed to fetch schemes:", error);
        setSchemes(getSchemesByRole(userRole));
      } finally {
        setIsLoading(false);
      }
    };

    fetchSchemes();
  }, [userRole]);
  
  const eligibleCount = schemes.filter(s => s.status === 'eligible').length;
  const conditionalCount = schemes.filter(s => s.status === 'conditional').length;
  const pendingSteps = mockActionSteps.filter(s => s.status === 'pending').length;
  const upcomingReminders = mockReminders.filter(r => r.status === 'pending').length;

  const quickStats = [
    {
      title: 'Eligible Schemes',
      value: isLoading ? '-' : eligibleCount,
      icon: CheckCircle2,
      color: 'text-success',
      bgColor: 'bg-success/10',
      link: '/dashboard/schemes'
    },
    {
      title: 'Conditional',
      value: isLoading ? '-' : conditionalCount,
      icon: AlertTriangle,
      color: 'text-warning',
      bgColor: 'bg-warning/10',
      link: '/dashboard/schemes'
    },
    {
      title: 'Pending Actions',
      value: pendingSteps,
      icon: ClipboardList,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
      link: '/dashboard/action-plan'
    },
    {
      title: 'Reminders',
      value: upcomingReminders,
      icon: Bell,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
      link: '/dashboard/reminders'
    },
  ];

  // Calculate Profile Completion
  const calculateCompletion = () => {
    if (!profile) return 0;
    
    const docs = profile.documents || {};
    const fields = [
      profile.fullName, profile.age, profile.gender, profile.dob,
      profile.mobileNumber, profile.email, profile.address, profile.state,
      profile.district, profile.pincode, profile.incomeRange, profile.occupation,
      profile.category, profile.familyStatus, profile.aadhaarNumber,
      profile.bankAccountNumber, profile.ifscCode,
      // Documents - safely accessed
      docs.aadhaarCard,
      docs.panCard,
      docs.incomeCertificate,
      docs.casteCertificate,
      docs.markSheet
    ];
    
    // Add occupation-specific fields
    if (profile.occupation === 'Student') {
      fields.push(profile.currentCourse);
      fields.push(profile.institution);
      fields.push(profile.education);
    } else if (profile.occupation === 'Farmer') {
      fields.push(profile.landHolding);
      fields.push(profile.farmingType);
    }

    const filled = fields.filter(f => f && f !== 0 && f !== '').length;
    const total = fields.length;
    return Math.round((filled / total) * 100);
  };

  const completionPercentage = calculateCompletion();
  const isProfileComplete = completionPercentage === 100;

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-6 md:py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            {userRole === 'student' ? (
              <GraduationCap className="h-8 w-8 text-primary" />
            ) : (
              <Wheat className="h-8 w-8 text-primary" />
            )}
            <div>
              <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground">
                Welcome, {user?.name?.split(' ')[0]}!
              </h1>
              <p className="text-muted-foreground">
                {userRole === 'student' 
                  ? 'Discover scholarships and education schemes for your future'
                  : 'Access agricultural schemes and farmer benefits'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {quickStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Link key={stat.title} to={stat.link}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.bgColor}`}>
                        <Icon className={`h-5 w-5 ${stat.color}`} />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                        <p className="text-xs text-muted-foreground">{stat.title}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>

        {/* Profile Completion & Quick Actions */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Profile Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <User className="h-5 w-5" />
                {isProfileComplete ? 'Your Profile' : 'Complete Your Profile'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isProfileComplete ? (
                <>
                  <div className="flex items-center gap-2 text-success mb-4">
                    <CheckCircle2 className="h-5 w-5" />
                    <span className="font-medium">Profile 100% Complete</span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    Your profile is up to date. You are getting the most accurate scheme recommendations.
                  </p>
                  <Link to="/dashboard/profile">
                    <Button variant="outline" className="w-full gap-2">
                      <Edit2 className="h-4 w-4" />
                      Edit Profile
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-4">
                    Complete your profile to get personalized scheme recommendations based on your details.
                  </p>
                  <Progress value={completionPercentage} className="mb-4" />
                  <p className="text-xs text-muted-foreground mb-4">{completionPercentage}% complete</p>
                  <Link to="/dashboard/profile">
                    <Button className="w-full gap-2">
                      Complete Profile
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </>
              )}
            </CardContent>
          </Card>

          {/* Schemes Overview */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="h-5 w-5" />
                {userRole === 'student' ? 'Student Schemes' : 'Farmer Schemes'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-4">
                    We found <span className="font-semibold text-foreground">{schemes.length} schemes</span> tailored for {userRole}s like you.
                  </p>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-success" />
                      <span className="text-sm">{eligibleCount} Eligible</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-warning" />
                      <span className="text-sm">{conditionalCount} Conditional</span>
                    </div>
                  </div>
                  <Link to="/dashboard/schemes">
                    <Button variant="outline" className="w-full gap-2">
                      View All Schemes
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Top Schemes Preview */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Top Recommended Schemes</CardTitle>
              <Link to="/dashboard/schemes">
                <Button variant="ghost" size="sm" className="gap-1">
                  View All
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <div className="space-y-3">
                {schemes.slice(0, 3).map((scheme) => (
                  <div 
                    key={scheme.id} 
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-foreground truncate">{scheme.name}</p>
                      <p className="text-sm text-muted-foreground">{scheme.benefits}</p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        scheme.status === 'eligible' 
                          ? 'bg-success/10 text-success' 
                          : 'bg-warning/10 text-warning'
                      }`}>
                        {scheme.status === 'eligible' ? 'Eligible' : 'Conditional'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
