import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { SchemeCard } from '@/components/schemes/SchemeCard';
import { SchemeDetailModal } from '@/components/schemes/SchemeDetailModal';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getSchemesByRole, Scheme } from '@/lib/mockData';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { Search, Filter, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

const categories = ['All', 'Agriculture', 'Education'];
const statuses = ['All', 'eligible', 'conditional', 'rejected'];

export default function Schemes() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');

  // Get schemes based on user role
  const userRole = user?.role || 'student';
  const roleSchemes = getSchemesByRole(userRole);
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
    <Layout>
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

        {/* Scheme Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredSchemes.map((scheme, index) => (
            <div key={scheme.id} className="animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
              <SchemeCard scheme={scheme} onViewDetails={setSelectedScheme} />
            </div>
          ))}
        </div>

        {filteredSchemes.length === 0 && (
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
    </Layout>
  );
}
