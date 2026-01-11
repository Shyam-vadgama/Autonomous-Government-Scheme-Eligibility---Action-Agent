import { useProfile } from '@/contexts/ProfileContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  MapPin, 
  Wallet, 
  Briefcase, 
  GraduationCap, 
  Users, 
  Accessibility,
  Edit2,
  CheckCircle2,
  Phone,
  Mail,
  CreditCard,
  FileText
} from 'lucide-react';

interface ProfileSummaryProps {
  onEdit: () => void;
  onProceed: () => void;
}

export function ProfileSummary({ onEdit, onProceed }: ProfileSummaryProps) {
  const { profile } = useProfile();

  const profileItems = [
    { 
      icon: User, 
      label: 'Personal', 
      value: `${profile.fullName || 'N/A'} (${profile.age}, ${profile.gender})` 
    },
    { icon: Phone, label: 'Mobile', value: profile.mobileNumber || 'N/A' },
    { icon: Mail, label: 'Email', value: profile.email || 'N/A' },
    { 
      icon: MapPin, 
      label: 'Address', 
      value: `${profile.address}, ${profile.district}, ${profile.state} - ${profile.pincode}` 
    },
    { icon: Wallet, label: 'Income', value: profile.incomeRange },
    { icon: Briefcase, label: 'Occupation', value: profile.occupation },
    { icon: Users, label: 'Family', value: profile.familyStatus },
    { icon: FileText, label: 'Aadhaar', value: profile.aadhaarNumber ? `XXXXXXXX${profile.aadhaarNumber.slice(-4)}` : 'N/A' },
  ];

  if (profile.occupation === 'Student') {
    profileItems.push({ icon: GraduationCap, label: 'Education', value: `${profile.education} (${profile.currentCourse})` });
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <Card className="shadow-card">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-success/10">
              <CheckCircle2 className="h-5 w-5 text-success" />
            </div>
            <div>
              <CardTitle className="font-display text-xl">Profile Complete</CardTitle>
              <p className="text-sm text-muted-foreground">Review your details below</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={onEdit} className="gap-2">
            <Edit2 className="h-4 w-4" />
            Edit
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            {profileItems.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                  <Icon className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-xs text-muted-foreground">{item.label}</p>
                    <p className="font-medium text-foreground truncate">{item.value}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
            <CreditCard className="h-5 w-5 text-primary shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Bank Details</p>
              <p className="font-medium text-foreground">
                {profile.bankAccountNumber ? `A/C: XXXXX${profile.bankAccountNumber.slice(-4)}` : 'N/A'} | IFSC: {profile.ifscCode || 'N/A'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
            <Accessibility className="h-5 w-5 text-primary shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Disability Status</p>
              <p className="font-medium text-foreground">
                {profile.disability ? 'Person with Disability' : 'Not Applicable'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 bg-primary/5 rounded-lg border border-primary/10">
            <Badge variant="category">{profile.category}</Badge>
            <span className="text-sm text-muted-foreground">Category</span>
          </div>

          <div className="flex flex-col gap-2 p-3 bg-muted/50 rounded-lg sm:col-span-2">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-4 w-4 text-primary" />
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Documents Uploaded</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {profile.documents && Object.entries(profile.documents).map(([key, value]) => (
                value ? (
                  <Badge key={key} variant="outline" className="bg-background text-xs font-normal border-success/30 text-success">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </Badge>
                ) : null
              ))}
              {(!profile.documents || Object.keys(profile.documents).length === 0) && (
                <span className="text-xs text-muted-foreground italic">No documents uploaded</span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Button variant="hero" size="xl" onClick={onProceed} className="w-full sm:w-auto">
          Proceed to Scheme Discovery
        </Button>
      </div>
    </div>
  );
}
