import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { SchemeCard } from '@/components/schemes/SchemeCard';
import { SchemeDetailModal } from '@/components/schemes/SchemeDetailModal';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getSchemesByRole, Scheme } from '@/lib/mockData';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { useProfile } from '@/contexts/ProfileContext';
import { api } from '@/lib/api';
import { Search, Filter, CheckCircle2, XCircle, AlertTriangle, Loader2 } from 'lucide-react';

const categories = ['All', 'Agriculture', 'Education'];
const statuses = ['All', 'eligible', 'conditional', 'rejected'];

export default function DashboardSchemes() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const { profile } = useProfile();
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  
  // State for schemes
  const [roleSchemes, setRoleSchemes] = useState<Scheme[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const userRole = user?.role || 'student';

  useEffect(() => {
    if (!user) return;

    const fetchSchemes = async () => {
      setIsLoading(true);
      try {
        // Pass current profile for dynamic eligibility
        const response = await api.schemes.getEligible(user.id, profile);
        const apiSchemes = response.discovered_schemes;
        const assessments = response.eligibility_assessments || [];
        
        if (apiSchemes && apiSchemes.length > 0) {
          // Map API response to Frontend Scheme interface
          const mappedSchemes: Scheme[] = apiSchemes.map((s: any, index) => {
            // Find assessment for this scheme if available
            const assessment = assessments.find((a: any) => a.scheme_id === s.scheme_id);
            
            return {
              id: s.scheme_id || `api-${index}`,
              name: s.name || s.title,
              category: s.category || 'General',
              targetGroup: (s.target_groups && s.target_groups.includes('student')) ? 'student' : 
                           (s.target_groups && s.target_groups.includes('farmer')) ? 'farmer' : 'both',
              description: s.description || s.snippet || '',
              benefits: s.benefits?.description || JSON.stringify(s.benefits) || 'View details',
              relevanceScore: assessment ? Math.round(assessment.confidence_score * 100) : (s.relevance_score ? Math.round(s.relevance_score * 100) : 0),
              status: assessment ? (assessment.overall_status === 'conditionally_eligible' ? 'conditional' : assessment.overall_status) : 'eligible',
              reason: assessment ? assessment.reason : (s.reason || 'Matched based on profile'),
              requiredDocuments: [], 
              applicationUrl: s.official_website || s.apply_link || s.source_url || null,
              conditionalNote: assessment?.missing_criteria?.join(', ')
            };
          });
          setRoleSchemes(mappedSchemes);
        } else {
          // Fallback to mock data if API returns empty
          console.log("API returned no schemes, using mock data");
          setRoleSchemes(getSchemesByRole(userRole));
        }
      } catch (error) {
        console.error("Failed to fetch schemes from API:", error);
        // Fallback to mock data on error
        setRoleSchemes(getSchemesByRole(userRole));
      } finally {
        setIsLoading(false);
      }
    };

    fetchSchemes();
  }, [user, profile]); // re-run when profile changes

  const filteredSchemes = roleSchemes.filter((scheme) => {
    const matchesSearch = scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         scheme.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || scheme.category === selectedCategory;
    const matchesStatus = selectedStatus === 'All' || scheme.status === selectedStatus;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const eligibleCount = roleSchemes.filter(s => s.status === 'eligible').length;
  const conditionalCount = roleSchemes.filter(s => s.status === 'conditional').length;
  const rejectedCount = roleSchemes.filter(s => s.status === 'rejected').length;

  return (
    <DashboardLayout>
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-2">
            {t('schemes.title')}
          </h1>
          <p className="text-muted-foreground">
            {t('schemes.subtitle').replace('{count}', String(roleSchemes.length))}
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-success/10 border border-success/20 rounded-xl p-4 flex items-center gap-3">
            <CheckCircle2 className="h-8 w-8 text-success" />
            <div>
              <p className="text-2xl font-bold text-foreground">{eligibleCount}</p>
              <p className="text-sm text-muted-foreground">{t('schemes.eligible')}</p>
            </div>
          </div>
          <div className="bg-warning/10 border border-warning/20 rounded-xl p-4 flex items-center gap-3">
            <AlertTriangle className="h-8 w-8 text-warning" />
            <div>
              <p className="text-2xl font-bold text-foreground">{conditionalCount}</p>
              <p className="text-sm text-muted-foreground">{t('schemes.conditional')}</p>
            </div>
          </div>
          <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 flex items-center gap-3">
            <XCircle className="h-8 w-8 text-destructive" />
            <div>
              <p className="text-2xl font-bold text-foreground">{rejectedCount}</p>
              <p className="text-sm text-muted-foreground">{t('schemes.notEligible')}</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-card rounded-xl border border-border p-4 mb-8 shadow-card">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={t('schemes.search')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <Filter className="h-4 w-4 text-muted-foreground" />
              {categories.map((cat) => (
                <Button
                  key={cat}
                  variant={selectedCategory === cat ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat === 'All' ? t('schemes.all') : cat}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 mt-4 flex-wrap">
            <span className="text-sm text-muted-foreground mr-2">{t('schemes.status')}</span>
            {statuses.map((status) => (
              <Badge
                key={status}
                variant={selectedStatus === status ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setSelectedStatus(status)}
              >
                {status === 'All' ? t('schemes.all') : status.charAt(0).toUpperCase() + status.slice(1)}
              </Badge>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Scheme Grid */}
        {!isLoading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSchemes.map((scheme, index) => (
              <div key={scheme.id} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <SchemeCard scheme={scheme} onViewDetails={setSelectedScheme} />
              </div>
            ))}
          </div>
        )}

        {!isLoading && filteredSchemes.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">{t('schemes.noResults')}</p>
          </div>
        )}

        <SchemeDetailModal
          scheme={selectedScheme}
          open={!!selectedScheme}
          onClose={() => setSelectedScheme(null)}
        />
      </div>
    </DashboardLayout>
  );
}
