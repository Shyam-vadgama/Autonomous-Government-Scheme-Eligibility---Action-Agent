import { useProfile } from '@/contexts/ProfileContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  indianStates,
  incomeRanges,
  categories,
  educationLevels,
  familyStatuses,
  studentCourses,
  landHoldings,
  farmingTypes,
} from '@/lib/mockData';
import { User, MapPin, Wallet, Briefcase, GraduationCap, Users, Accessibility, ChevronRight, ChevronLeft, Wheat, CreditCard, Mail, Phone, FileText, Upload } from 'lucide-react';
import { cn } from '@/lib/utils';

const formSteps = [
  { id: 'personal', title: 'Personal & Identity', icon: User },
  { id: 'contact', title: 'Contact & Location', icon: MapPin },
  { id: 'details', title: 'Role & Bank Details', icon: Briefcase },
  { id: 'documents', title: 'Documents', icon: FileText },
];

interface ProfileFormProps {
  onComplete: () => void;
}

export function ProfileForm({ onComplete }: ProfileFormProps) {
  const { profile, updateProfile, currentStep, setCurrentStep } = useProfile();
  const { user } = useAuth();

  // Set occupation from user role
  const userRole = user?.role || 'student';
  const occupation = userRole === 'student' ? 'Student' : 'Farmer';

  const handleNext = () => {
    // Ensure occupation is set based on user role
    if (profile.occupation !== occupation) {
      updateProfile({ occupation });
    }
    
    if (currentStep < formSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFileChange = (docType: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      updateProfile({
        documents: {
          ...(profile.documents || {}),
          [docType]: file.name // Store filename as simulation
        }
      });
    }
  };

  const calculateAge = (dob: string) => {
    if (!dob) return 0;
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return Math.max(0, age);
  };

  return (
    <div className="space-y-8">
      {/* Progress Steps */}
      <div className="flex items-center justify-center gap-2">
        {formSteps.map((step, index) => {
          const StepIcon = step.icon;
          const isActive = index === currentStep;
          const isComplete = index < currentStep;
          
          return (
            <div key={step.id} className="flex items-center">
              <button
                onClick={() => setCurrentStep(index)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
                  isActive 
                    ? "bg-primary text-primary-foreground" 
                    : isComplete 
                    ? "bg-success/10 text-success" 
                    : "bg-muted text-muted-foreground"
                )}
              >
                <StepIcon className="h-4 w-4" />
                <span className="hidden sm:inline font-medium">{step.title}</span>
              </button>
              {index < formSteps.length - 1 && (
                <div className={cn(
                  "w-8 h-0.5 mx-2",
                  isComplete ? "bg-success" : "bg-muted"
                )} />
              )}
            </div>
          );
        })}
      </div>

      {/* Form Content */}
      <div className="bg-card rounded-xl border border-border p-6 shadow-card animate-fade-in">
        {currentStep === 0 && (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                placeholder="Enter your full name as per Aadhaar"
                value={profile.fullName || ''}
                onChange={(e) => updateProfile({ fullName: e.target.value })}
              />
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="dob">Date of Birth</Label>
                <Input
                  id="dob"
                  type="date"
                  value={profile.dob || ''}
                  onChange={(e) => {
                    const dob = e.target.value;
                    const age = calculateAge(dob);
                    updateProfile({ dob, age });
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  type="number"
                  placeholder="Age"
                  value={profile.age || ''}
                  onChange={(e) => updateProfile({ age: parseInt(e.target.value) || 0 })}
                  min={1}
                  max={120}
                />
              </div>
            </div>
              
            <div className="space-y-2">
              <Label>Gender</Label>
              <RadioGroup
                value={profile.gender}
                onValueChange={(value) => updateProfile({ gender: value as any })}
                className="flex gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="male" id="male" />
                  <Label htmlFor="male" className="cursor-pointer">Male</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="female" id="female" />
                  <Label htmlFor="female" className="cursor-pointer">Female</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="other" id="other" />
                  <Label htmlFor="other" className="cursor-pointer">Other</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-2">
              <Label htmlFor="aadhaar">Aadhaar Number</Label>
              <Input
                id="aadhaar"
                type="text"
                maxLength={12}
                placeholder="12-digit Aadhaar Number"
                value={profile.aadhaarNumber || ''}
                onChange={(e) => updateProfile({ aadhaarNumber: e.target.value })}
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <Accessibility className="h-5 w-5 text-muted-foreground" />
                <div>
                  <Label htmlFor="disability" className="cursor-pointer">Person with Disability</Label>
                  <p className="text-xs text-muted-foreground">Select if applicable for special schemes</p>
                </div>
              </div>
              <Switch
                id="disability"
                checked={profile.disability}
                onCheckedChange={(checked) => updateProfile({ disability: checked })}
              />
            </div>
          </div>
        )}

        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="mobile" className="flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Mobile Number
                </Label>
                <Input
                  id="mobile"
                  type="tel"
                  placeholder="10-digit Mobile Number"
                  value={profile.mobileNumber || ''}
                  onChange={(e) => updateProfile({ mobileNumber: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="email@example.com"
                  value={profile.email || ''}
                  onChange={(e) => updateProfile({ email: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Address
              </Label>
              <Input
                placeholder="House No, Street, Village/City"
                value={profile.address || ''}
                onChange={(e) => updateProfile({ address: e.target.value })}
              />
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>State</Label>
                <Select
                  value={profile.state}
                  onValueChange={(value) => updateProfile({ state: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your state" />
                  </SelectTrigger>
                  <SelectContent>
                    {indianStates.map((state) => (
                      <SelectItem key={state} value={state}>{state}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>District</Label>
                <Input
                  placeholder="Enter District"
                  value={profile.district || ''}
                  onChange={(e) => updateProfile({ district: e.target.value })}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label>Pincode</Label>
              <Input
                placeholder="6-digit Pincode"
                maxLength={6}
                value={profile.pincode || ''}
                onChange={(e) => updateProfile({ pincode: e.target.value })}
              />
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-6">
            {/* Role indicator */}
            <div className="flex items-center gap-3 p-4 bg-primary/5 border border-primary/20 rounded-lg">
              {userRole === 'student' ? (
                <GraduationCap className="h-6 w-6 text-primary" />
              ) : (
                <Wheat className="h-6 w-6 text-primary" />
              )}
              <div>
                <p className="font-medium text-foreground">
                  {userRole === 'student' ? 'Student Profile' : 'Farmer Profile'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Complete your {userRole} details for personalized scheme matching
                </p>
              </div>
            </div>

            <div className="grid gap-6 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Category</Label>
                <Select
                  value={profile.category}
                  onValueChange={(value) => updateProfile({ category: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select your category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label className="flex items-center gap-2">
                  <Wallet className="h-4 w-4" />
                  Annual Family Income
                </Label>
                <Select
                  value={profile.incomeRange}
                  onValueChange={(value) => updateProfile({ incomeRange: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select income range" />
                  </SelectTrigger>
                  <SelectContent>
                    {incomeRanges.map((range) => (
                      <SelectItem key={range} value={range}>{range}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Student-specific fields */}
            {userRole === 'student' && (
              <>
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <GraduationCap className="h-4 w-4" />
                    Current Course/Class
                  </Label>
                  <Select
                    value={profile.currentCourse || ''}
                    onValueChange={(value) => updateProfile({ currentCourse: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your current course" />
                    </SelectTrigger>
                    <SelectContent>
                      {studentCourses.map((course) => (
                        <SelectItem key={course} value={course}>{course}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Institution Name</Label>
                  <Input 
                    placeholder="School/College/University Name"
                    value={profile.institution || ''}
                    onChange={(e) => updateProfile({ institution: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <GraduationCap className="h-4 w-4" />
                    Education Level
                  </Label>
                  <Select
                    value={profile.education}
                    onValueChange={(value) => updateProfile({ education: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select education level" />
                    </SelectTrigger>
                    <SelectContent>
                      {educationLevels.map((edu) => (
                        <SelectItem key={edu} value={edu}>{edu}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            {/* Farmer-specific fields */}
            {userRole === 'farmer' && (
              <>
                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Wheat className="h-4 w-4" />
                    Land Holding
                  </Label>
                  <Select
                    value={profile.landHolding || ''}
                    onValueChange={(value) => updateProfile({ landHolding: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select land holding category" />
                    </SelectTrigger>
                    <SelectContent>
                      {landHoldings.map((holding) => (
                        <SelectItem key={holding} value={holding}>{holding}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="flex items-center gap-2">
                    <Wheat className="h-4 w-4" />
                    Type of Farming
                  </Label>
                  <Select
                    value={profile.farmingType || ''}
                    onValueChange={(value) => updateProfile({ farmingType: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select farming type" />
                    </SelectTrigger>
                    <SelectContent>
                      {farmingTypes.map((type) => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                Family Status
              </Label>
              <Select
                value={profile.familyStatus}
                onValueChange={(value) => updateProfile({ familyStatus: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select family status" />
                </SelectTrigger>
                <SelectContent>
                  {familyStatuses.map((status) => (
                    <SelectItem key={status} value={status}>{status}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="p-4 bg-muted/50 rounded-lg space-y-4 border border-border">
              <h4 className="font-medium flex items-center gap-2">
                <CreditCard className="h-4 w-4" />
                Bank Details (for DBT)
              </h4>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label>Account Number</Label>
                  <Input 
                    placeholder="Bank Account Number"
                    value={profile.bankAccountNumber || ''}
                    onChange={(e) => updateProfile({ bankAccountNumber: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>IFSC Code</Label>
                  <Input 
                    placeholder="IFSC Code"
                    value={profile.ifscCode || ''}
                    onChange={(e) => updateProfile({ ifscCode: e.target.value })}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="bg-primary/5 p-4 rounded-lg border border-primary/20 mb-6">
              <h4 className="font-medium flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-primary" />
                Mandatory Documents
              </h4>
              <p className="text-sm text-muted-foreground">
                Please upload these essential documents to verify your eligibility. These are final for all users. 
                Additional documents may be requested for specific schemes later.
              </p>
            </div>

            <div className="space-y-4">
              {[
                { id: 'aadhaarCard', label: 'Aadhaar Card' },
                { id: 'panCard', label: 'PAN Card' },
                { id: 'incomeCertificate', label: 'Income Certificate' },
                { id: 'casteCertificate', label: 'Caste Certificate' },
                { id: 'markSheet', label: 'Previous Marksheet' },
              ].map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-4 border border-border rounded-lg bg-card hover:bg-muted/30 transition-colors">
                  <div className="flex-1">
                    <Label htmlFor={doc.id} className="text-base font-medium cursor-pointer">
                      {doc.label}
                    </Label>
                    <p className="text-xs text-muted-foreground mt-1">
                      {profile.documents?.[doc.id] 
                        ? <span className="text-success font-medium flex items-center gap-1">File selected: {profile.documents[doc.id]}</span> 
                        : "No file selected"}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Input
                      id={doc.id}
                      type="file"
                      className="hidden"
                      onChange={(e) => handleFileChange(doc.id, e)}
                    />
                    <Button variant="outline" size="sm" onClick={() => document.getElementById(doc.id)?.click()}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between gap-4">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 0}
          className="gap-2"
        >
          <ChevronLeft className="h-4 w-4" />
          Back
        </Button>
        <Button
          variant="hero"
          onClick={handleNext}
          className="gap-2"
        >
          {currentStep === formSteps.length - 1 ? 'Complete Profile' : 'Next Step'}
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
