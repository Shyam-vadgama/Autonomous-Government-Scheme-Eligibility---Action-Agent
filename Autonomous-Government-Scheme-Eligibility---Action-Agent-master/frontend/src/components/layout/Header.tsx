import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Shield, Menu, X, ChevronRight, Globe, Type, Plus, Minus, LogIn, LogOut, GraduationCap, Wheat } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAccessibility } from '@/contexts/AccessibilityContext';
import { useAuth } from '@/contexts/AuthContext';

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();
  const { fontSize, increaseFontSize, decreaseFontSize } = useAccessibility();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-card border-b border-border shadow-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-hero">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div className="hidden sm:block">
            <h1 className="font-display text-lg font-bold text-foreground">
              GovScheme
            </h1>
            <p className="text-xs text-muted-foreground">
              For Students & Farmers
            </p>
          </div>
        </Link>

        {/* Right side controls */}
        <div className="hidden md:flex items-center gap-3">
          {/* Font Size Controls */}
          <div className="flex items-center gap-1 border border-border rounded-lg p-1">
            <button
              onClick={decreaseFontSize}
              disabled={fontSize === 'small'}
              className="p-1.5 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
              aria-label="Decrease font size"
            >
              <Minus className="h-3.5 w-3.5" />
            </button>
            <Type className="h-4 w-4 text-muted-foreground mx-1" />
            <button
              onClick={increaseFontSize}
              disabled={fontSize === 'xlarge'}
              className="p-1.5 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
              aria-label="Increase font size"
            >
              <Plus className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Language Toggle */}
          <div className="flex items-center border border-border rounded-lg overflow-hidden">
            <button
              onClick={() => setLanguage('en')}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition-colors flex items-center gap-1.5",
                language === 'en' 
                  ? "bg-primary text-primary-foreground" 
                  : "text-foreground hover:bg-muted"
              )}
            >
              <Globe className="h-3.5 w-3.5" />
              EN
            </button>
            <button
              onClick={() => setLanguage('hi')}
              className={cn(
                "px-3 py-1.5 text-xs font-medium transition-colors",
                language === 'hi' 
                  ? "bg-primary text-primary-foreground" 
                  : "text-foreground hover:bg-muted"
              )}
            >
              हिं
            </button>
          </div>

          {/* Auth Buttons */}
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <Link to="/dashboard">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-lg hover:bg-muted/80 transition-colors cursor-pointer">
                  {user?.role === 'student' ? (
                    <GraduationCap className="h-4 w-4 text-primary" />
                  ) : (
                    <Wheat className="h-4 w-4 text-primary" />
                  )}
                  <span className="text-sm font-medium text-foreground">{user?.name?.split(' ')[0]}</span>
                </div>
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout} className="gap-2">
                <LogOut className="h-4 w-4" />
                {t('auth.logout')}
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login">
                <Button variant="outline" size="sm" className="gap-2">
                  <LogIn className="h-4 w-4" />
                  Sign In
                </Button>
              </Link>
              <Link to="/register">
                <Button size="sm" className="gap-2">
                  {t('nav.getStarted')}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden text-foreground"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border bg-card">
          <nav className="container mx-auto flex flex-col p-4 gap-3">
            {/* Mobile accessibility controls */}
            <div className="flex items-center justify-between px-2">
              <span className="text-sm text-muted-foreground flex items-center gap-2">
                <Type className="h-4 w-4" />
                {t('accessibility.fontSize')}
              </span>
              <div className="flex items-center gap-1 border border-border rounded-lg p-1">
                <button
                  onClick={decreaseFontSize}
                  disabled={fontSize === 'small'}
                  className="p-1.5 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
                >
                  <Minus className="h-3.5 w-3.5" />
                </button>
                <span className="px-2 text-xs text-foreground font-medium">
                  {fontSize === 'normal' ? 'A' : fontSize === 'small' ? 'A-' : fontSize === 'large' ? 'A+' : 'A++'}
                </span>
                <button
                  onClick={increaseFontSize}
                  disabled={fontSize === 'xlarge'}
                  className="p-1.5 rounded hover:bg-muted disabled:opacity-40 transition-colors text-foreground"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center justify-between px-2">
              <span className="text-sm text-muted-foreground flex items-center gap-2">
                <Globe className="h-4 w-4" />
                {t('accessibility.language')}
              </span>
              <div className="flex items-center border border-border rounded-lg overflow-hidden">
                <button
                  onClick={() => setLanguage('en')}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium transition-colors",
                    language === 'en' 
                      ? "bg-primary text-primary-foreground" 
                      : "text-foreground hover:bg-muted"
                  )}
                >
                  English
                </button>
                <button
                  onClick={() => setLanguage('hi')}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium transition-colors",
                    language === 'hi' 
                      ? "bg-primary text-primary-foreground" 
                      : "text-foreground hover:bg-muted"
                  )}
                >
                  हिंदी
                </button>
              </div>
            </div>

            {/* Mobile Auth */}
            <div className="pt-2 border-t border-border space-y-2">
              {isAuthenticated ? (
                <>
                  <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>
                    <div className="flex items-center gap-2 px-4 py-2 bg-muted rounded-lg">
                      {user?.role === 'student' ? (
                        <GraduationCap className="h-4 w-4 text-primary" />
                      ) : (
                        <Wheat className="h-4 w-4 text-primary" />
                      )}
                      <span className="text-sm font-medium text-foreground">{user?.name}</span>
                      <span className="text-xs text-muted-foreground capitalize">({user?.role})</span>
                    </div>
                  </Link>
                  <Button variant="outline" size="lg" className="w-full gap-2" onClick={handleLogout}>
                    <LogOut className="h-4 w-4" />
                    {t('auth.logout')}
                  </Button>
                </>
              ) : (
                <>
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="outline" size="lg" className="w-full gap-2">
                      <LogIn className="h-4 w-4" />
                      Sign In
                    </Button>
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="default" size="lg" className="w-full gap-2">
                      {t('nav.getStarted')}
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
