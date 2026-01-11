import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type FontSize = 'small' | 'normal' | 'large' | 'xlarge';

interface AccessibilityContextType {
  fontSize: FontSize;
  setFontSize: (size: FontSize) => void;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
  resetFontSize: () => void;
}

const fontSizeMap: Record<FontSize, string> = {
  small: '14px',
  normal: '16px',
  large: '18px',
  xlarge: '20px',
};

const fontSizeOrder: FontSize[] = ['small', 'normal', 'large', 'xlarge'];

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export function AccessibilityProvider({ children }: { children: ReactNode }) {
  const [fontSize, setFontSize] = useState<FontSize>('normal');

  useEffect(() => {
    document.documentElement.style.fontSize = fontSizeMap[fontSize];
  }, [fontSize]);

  const increaseFontSize = () => {
    const currentIndex = fontSizeOrder.indexOf(fontSize);
    if (currentIndex < fontSizeOrder.length - 1) {
      setFontSize(fontSizeOrder[currentIndex + 1]);
    }
  };

  const decreaseFontSize = () => {
    const currentIndex = fontSizeOrder.indexOf(fontSize);
    if (currentIndex > 0) {
      setFontSize(fontSizeOrder[currentIndex - 1]);
    }
  };

  const resetFontSize = () => {
    setFontSize('normal');
  };

  return (
    <AccessibilityContext.Provider value={{ 
      fontSize, 
      setFontSize, 
      increaseFontSize, 
      decreaseFontSize, 
      resetFontSize 
    }}>
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}
