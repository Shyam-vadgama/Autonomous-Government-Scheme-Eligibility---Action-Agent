import { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  User, 
  FileText, 
  ClipboardList, 
  Bell, 
  LogOut,
  Menu,
  X,
  GraduationCap,
  Wheat,
  Globe,
  Type,
  Plus,
  Minus
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAccessibility } from '@/contexts/AccessibilityContext';
import { useState } from 'react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const { fontSize, increaseFontSize, decreaseFontSize } = useAccessibility();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/dashboard/profile', label: t('nav.profile'), icon: User },
    { path: '/dashboard/schemes', label: t('nav.schemes'), icon: FileText },
    { path: '/dashboard/action-plan', label: t('nav.actionPlan'), icon: ClipboardList },
    { path: '/dashboard/reminders', label: t('nav.reminders'), icon: Bell },
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      <header className="lg:hidden sticky top-0 z-50 w-full bg-card border-b border-border shadow-sm">
        <div className="flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg gradient-hero">
                <Shield className="h-4 w-4 text-white" />
              </div>
              <span className="font-display font-bold text-foreground">GovScheme</span>
            </Link>
          </div>
          <div className="flex items-center gap-2">
            {user?.role === 'student' ? (
              <GraduationCap className="h-5 w-5 text-primary" />
            ) : (
              <Wheat className="h-5 w-5 text-primary" />
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border transform transition-transform duration-200 lg:translate-x-0 lg:static lg:inset-auto",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <div className="flex flex-col h-full">
            {/* Sidebar Header */}
            <div className="hidden lg:flex items-center gap-3 p-4 border-b border-border">
              <Link to="/dashboard" className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-hero">
                  <Shield className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h1 className="font-display text-lg font-bold text-foreground">
                    GovScheme
                  </h1>
                  <p className="text-xs text-muted-foreground">
                    For Students & Farmers
                  </p>
                </div>
              </Link>
            </div>

            {/* User Info */}
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                {user?.role === 'student' ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <GraduationCap className="h-5 w-5 text-primary" />
                  </div>
                ) : (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Wheat className="h-5 w-5 text-primary" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground truncate">{user?.name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setSidebarOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "text-foreground hover:bg-muted"
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-border space-y-3">
              {/* Language Toggle */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  {t('accessibility.language')}
                </span>
                <div className="flex items-center border border-border rounded-lg overflow-hidden">
                  <button
                    onClick={() => setLanguage('en')}
                    className={cn(
                      "px-2 py-1 text-xs font-medium transition-colors",
                      language === 'en' 
                        ? "bg-primary text-primary-foreground" 
                        : "text-foreground hover:bg-muted"
                    )}
                  >
                    EN
                  </button>
                  <button
                    onClick={() => setLanguage('hi')}
                    className={cn(
                      "px-2 py-1 text-xs font-medium transition-colors",
                      language === 'hi' 
                        ? "bg-primary text-primary-foreground" 
                        : "text-foreground hover:bg-muted"
                    )}
                  >
                    हिं
                  </button>
                </div>
              </div>

              {/* Font Size */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground flex items-center gap-2">
                  <Type className="h-4 w-4" />
                  Font
                </span>
                <div className="flex items-center gap-1 border border-border rounded-lg p-1">
                  <button
                    onClick={decreaseFontSize}
                    disabled={fontSize === 'small'}
                    className="p-1 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
                  >
                    <Minus className="h-3 w-3" />
                  </button>
                  <button
                    onClick={increaseFontSize}
                    disabled={fontSize === 'xlarge'}
                    className="p-1 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
                  >
                    <Plus className="h-3 w-3" />
                  </button>
                </div>
              </div>

              {/* Logout */}
              <Button 
                variant="outline" 
                className="w-full gap-2" 
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4" />
                {t('auth.logout')}
              </Button>
            </div>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 min-h-screen lg:min-h-[calc(100vh)]">
          {children}
        </main>
      </div>
    </div>
  );
}
