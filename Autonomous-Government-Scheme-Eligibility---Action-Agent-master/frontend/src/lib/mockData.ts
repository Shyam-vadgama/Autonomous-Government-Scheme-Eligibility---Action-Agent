// Mock data for the Government Scheme Eligibility Platform
// Focused on Students and Farmers only

export interface CitizenProfile {
  // Basic Demographics
  fullName: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  dob: string; // YYYY-MM-DD
  
  // Contact & Location
  mobileNumber: string;
  email: string;
  address: string;
  state: string;
  district: string;
  pincode: string;
  
  // Socio-Economic
  incomeRange: string;
  occupation: 'Student' | 'Farmer';
  category: string;
  disability: boolean;
  familyStatus: string;
  
  // Education (Student)
  education: string;
  currentCourse?: string;
  institution?: string;
  
  // Agriculture (Farmer)
  landHolding?: string;
  farmingType?: string;
  
  // Identification & Banking
  aadhaarNumber: string;
  bankAccountNumber: string;
  ifscCode: string;
}

export interface Scheme {
  id: string;
  name: string;
  category: string;
  targetGroup: 'student' | 'farmer' | 'both';
  description: string;
  benefits: string;
  relevanceScore: number;
  status: 'eligible' | 'rejected' | 'conditional';
  reason: string;
  requiredDocuments: Document[];
  conditionalNote?: string;
  applicationUrl?: string;
}

export interface Document {
  id: string;
  name: string;
  available: boolean;
  mandatory: boolean;
}

export interface ActionStep {
  id: string;
  schemeId: string;
  schemeName: string;
  step: number;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  estimatedTime: string;
  status: 'pending' | 'in-progress' | 'completed';
}

export interface Reminder {
  id: string;
  title: string;
  description: string;
  date: string;
  type: 'deadline' | 'follow-up' | 'document' | 'update';
  status: 'pending' | 'completed';
}

export const indianStates = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
  'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
  'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  'Delhi', 'Jammu and Kashmir', 'Ladakh'
];

export const incomeRanges = [
  'Below ₹1,00,000',
  '₹1,00,000 - ₹2,50,000',
  '₹2,50,000 - ₹5,00,000',
  '₹5,00,000 - ₹10,00,000',
  'Above ₹10,00,000'
];

export const categories = [
  'General',
  'OBC (Other Backward Classes)',
  'SC (Scheduled Caste)',
  'ST (Scheduled Tribe)',
  'EWS (Economically Weaker Section)'
];

export const educationLevels = [
  'No Formal Education',
  'Primary (1-5)',
  'Secondary (6-10)',
  'Higher Secondary (11-12)',
  'Diploma',
  'Graduate',
  'Post Graduate',
  'Doctorate'
];

export const familyStatuses = [
  'Single',
  'Married',
  'Widowed',
  'Divorced',
  'Separated'
];

// Student-specific options
export const studentCourses = [
  'Class 9-10',
  'Class 11-12',
  'Undergraduate (BA/BSc/BCom)',
  'Engineering (BTech/BE)',
  'Medical (MBBS/BDS)',
  'Diploma/ITI',
  'Post Graduate',
  'PhD/Research',
  'Professional Courses'
];

// Farmer-specific options
export const landHoldings = [
  'Landless',
  'Marginal (Below 1 hectare)',
  'Small (1-2 hectares)',
  'Semi-Medium (2-4 hectares)',
  'Medium (4-10 hectares)',
  'Large (Above 10 hectares)'
];

export const farmingTypes = [
  'Crop Farming',
  'Horticulture',
  'Dairy Farming',
  'Poultry',
  'Fisheries',
  'Mixed Farming',
  'Organic Farming'
];

// Student Schemes
export const studentSchemes: Scheme[] = [
  {
    id: 's1',
    name: 'National Scholarship Portal (NSP)',
    category: 'Education',
    targetGroup: 'student',
    description: 'Central government scholarships for students from economically weaker sections pursuing higher education.',
    benefits: 'Up to ₹75,000 per annum for tuition and maintenance',
    relevanceScore: 95,
    status: 'eligible',
    reason: 'You meet all eligibility criteria: enrolled in recognized institution, family income below threshold.',
    requiredDocuments: [
      { id: 'd1', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd2', name: 'Previous Year Marksheet', available: true, mandatory: true },
      { id: 'd3', name: 'Income Certificate', available: false, mandatory: true },
      { id: 'd4', name: 'Caste Certificate', available: true, mandatory: false }
    ]
  },
  {
    id: 's2',
    name: 'PM Vidyalakshmi Education Loan',
    category: 'Education',
    targetGroup: 'student',
    description: 'Interest subsidy on education loans for students from economically weaker sections.',
    benefits: 'Full interest subsidy during moratorium period',
    relevanceScore: 88,
    status: 'eligible',
    reason: 'You qualify for interest subsidy based on family income and enrollment in eligible course.',
    requiredDocuments: [
      { id: 'd5', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd6', name: 'Admission Letter', available: true, mandatory: true },
      { id: 'd7', name: 'Income Certificate', available: false, mandatory: true },
      { id: 'd8', name: 'Bank Account Details', available: true, mandatory: true }
    ]
  },
  {
    id: 's3',
    name: 'Post Matric Scholarship (SC/ST/OBC)',
    category: 'Education',
    targetGroup: 'student',
    description: 'Scholarship for SC/ST/OBC students pursuing post-matriculation studies.',
    benefits: '₹12,000 - ₹30,000 annually based on course',
    relevanceScore: 92,
    status: 'conditional',
    reason: 'You meet income criteria. Verification of caste certificate required.',
    conditionalNote: 'Please provide valid caste certificate issued by competent authority.',
    requiredDocuments: [
      { id: 'd9', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd10', name: 'Caste Certificate', available: false, mandatory: true },
      { id: 'd11', name: 'Income Certificate', available: false, mandatory: true },
      { id: 'd12', name: 'Fee Receipt', available: true, mandatory: true }
    ]
  },
  {
    id: 's4',
    name: 'INSPIRE Scholarship',
    category: 'Education',
    targetGroup: 'student',
    description: 'Scholarship for meritorious students pursuing natural and basic sciences at graduation level.',
    benefits: '₹80,000 per annum (₹60,000 scholarship + ₹20,000 summer project)',
    relevanceScore: 75,
    status: 'conditional',
    reason: 'Eligible if pursuing BSc in natural sciences with top 1% marks in 12th.',
    conditionalNote: 'Provide proof of marks in top 1% of your board examination.',
    requiredDocuments: [
      { id: 'd13', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd14', name: '12th Marksheet', available: true, mandatory: true },
      { id: 'd15', name: 'Admission Proof in Science Course', available: true, mandatory: true }
    ]
  },
  {
    id: 's5',
    name: 'Central Sector Scholarship',
    category: 'Education',
    targetGroup: 'student',
    description: 'Merit-based scholarship for students from low-income families scoring above 80 percentile.',
    benefits: '₹12,000 per annum for graduation, ₹20,000 for post-graduation',
    relevanceScore: 85,
    status: 'eligible',
    reason: 'You meet merit and income criteria for this scholarship.',
    requiredDocuments: [
      { id: 'd16', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd17', name: '12th Marksheet', available: true, mandatory: true },
      { id: 'd18', name: 'Income Certificate', available: false, mandatory: true },
      { id: 'd19', name: 'Current Year Admission Proof', available: true, mandatory: true }
    ]
  },
  {
    id: 's6',
    name: 'Pragati Scholarship for Girls',
    category: 'Education',
    targetGroup: 'student',
    description: 'AICTE scholarship for girl students in technical education to promote women in engineering.',
    benefits: '₹50,000 per annum for 4 years',
    relevanceScore: 90,
    status: 'eligible',
    reason: 'You are eligible as a female student in technical education with family income below ₹8 lakh.',
    requiredDocuments: [
      { id: 'd20', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd21', name: 'Income Certificate', available: false, mandatory: true },
      { id: 'd22', name: 'Institution Verification Letter', available: true, mandatory: true }
    ]
  }
];

// Farmer Schemes
export const farmerSchemes: Scheme[] = [
  {
    id: 'f1',
    name: 'PM Kisan Samman Nidhi',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Direct income support of ₹6,000 per year to small and marginal farmer families.',
    benefits: '₹6,000 per year in three equal installments',
    relevanceScore: 95,
    status: 'eligible',
    reason: 'You meet all eligibility criteria: registered farmer with cultivable land under 2 hectares.',
    requiredDocuments: [
      { id: 'd23', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd24', name: 'Land Ownership Documents', available: true, mandatory: true },
      { id: 'd25', name: 'Bank Account Details', available: true, mandatory: true },
      { id: 'd26', name: 'Recent Passport Photo', available: false, mandatory: true }
    ]
  },
  {
    id: 'f2',
    name: 'PM Fasal Bima Yojana',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Crop insurance scheme providing financial support in case of crop failure due to natural calamities.',
    benefits: 'Insurance coverage for crops at nominal premium (1.5% - 2%)',
    relevanceScore: 92,
    status: 'eligible',
    reason: 'You are eligible as a farmer growing notified crops in your area.',
    requiredDocuments: [
      { id: 'd27', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd28', name: 'Land Records (Khata/Khasra)', available: true, mandatory: true },
      { id: 'd29', name: 'Sowing Certificate', available: false, mandatory: true },
      { id: 'd30', name: 'Bank Account Details', available: true, mandatory: true }
    ]
  },
  {
    id: 'f3',
    name: 'Kisan Credit Card (KCC)',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Credit facility for farmers to meet their cultivation expenses and other needs.',
    benefits: 'Credit limit up to ₹3 lakh at 4% interest rate',
    relevanceScore: 90,
    status: 'eligible',
    reason: 'You qualify for KCC based on your land holding and farming activity.',
    requiredDocuments: [
      { id: 'd31', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd32', name: 'Land Documents', available: true, mandatory: true },
      { id: 'd33', name: 'Passport Photo', available: false, mandatory: true },
      { id: 'd34', name: 'Bank Passbook', available: true, mandatory: true }
    ]
  },
  {
    id: 'f4',
    name: 'PM Kisan Maandhan Yojana',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Pension scheme for small and marginal farmers providing assured pension after 60 years of age.',
    benefits: '₹3,000 per month pension after age 60',
    relevanceScore: 85,
    status: 'conditional',
    reason: 'Eligible if age is between 18-40 years with small/marginal land holding.',
    conditionalNote: 'Verify age and land holding documents to confirm eligibility.',
    requiredDocuments: [
      { id: 'd35', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd36', name: 'Land Records', available: true, mandatory: true },
      { id: 'd37', name: 'Age Proof', available: true, mandatory: true }
    ]
  },
  {
    id: 'f5',
    name: 'Soil Health Card Scheme',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Free soil testing and health card to help farmers use appropriate fertilizers.',
    benefits: 'Free soil testing and personalized fertilizer recommendations',
    relevanceScore: 88,
    status: 'eligible',
    reason: 'All farmers are eligible for this scheme.',
    requiredDocuments: [
      { id: 'd38', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd39', name: 'Land Records', available: true, mandatory: true }
    ]
  },
  {
    id: 'f6',
    name: 'PM Krishi Sinchai Yojana',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Subsidy for micro-irrigation systems like drip and sprinkler irrigation.',
    benefits: '55%-75% subsidy on micro-irrigation systems',
    relevanceScore: 80,
    status: 'eligible',
    reason: 'You are eligible for irrigation subsidy based on your land holding.',
    requiredDocuments: [
      { id: 'd40', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd41', name: 'Land Ownership Documents', available: true, mandatory: true },
      { id: 'd42', name: 'Bank Account Details', available: true, mandatory: true }
    ]
  },
  {
    id: 'f7',
    name: 'Paramparagat Krishi Vikas Yojana',
    category: 'Agriculture',
    targetGroup: 'farmer',
    description: 'Support for organic farming with assistance for certification and inputs.',
    benefits: '₹50,000 per hectare over 3 years for organic farming',
    relevanceScore: 75,
    status: 'conditional',
    reason: 'Eligible if practicing or willing to adopt organic farming in a cluster.',
    conditionalNote: 'Join or form a cluster of 50+ farmers for group certification.',
    requiredDocuments: [
      { id: 'd43', name: 'Aadhaar Card', available: true, mandatory: true },
      { id: 'd44', name: 'Land Records', available: true, mandatory: true },
      { id: 'd45', name: 'Cluster Formation Document', available: false, mandatory: true }
    ]
  }
];

// Combined schemes function
export const getSchemesByRole = (role: 'student' | 'farmer' | 'both'): Scheme[] => {
  if (role === 'student') return studentSchemes;
  if (role === 'farmer') return farmerSchemes;
  return [...studentSchemes, ...farmerSchemes];
};

// Backward compatibility
export const mockSchemes: Scheme[] = [...studentSchemes, ...farmerSchemes];

export const mockActionSteps: ActionStep[] = [
  // Student action steps
  {
    id: 'a1',
    schemeId: 's1',
    schemeName: 'National Scholarship Portal',
    step: 1,
    title: 'Gather Required Documents',
    description: 'Collect Aadhaar card, marksheets, and income certificate from Tehsil office.',
    priority: 'high',
    estimatedTime: '3-5 days',
    status: 'pending'
  },
  {
    id: 'a2',
    schemeId: 's1',
    schemeName: 'National Scholarship Portal',
    step: 2,
    title: 'Register on NSP Portal',
    description: 'Create account on scholarships.gov.in and complete profile.',
    priority: 'high',
    estimatedTime: '30 minutes',
    status: 'pending'
  },
  {
    id: 'a3',
    schemeId: 's2',
    schemeName: 'PM Vidyalakshmi Education Loan',
    step: 1,
    title: 'Register on Vidyalakshmi Portal',
    description: 'Create account on vidyalakshmi.co.in and explore loan options.',
    priority: 'high',
    estimatedTime: '1 hour',
    status: 'pending'
  },
  // Farmer action steps
  {
    id: 'a4',
    schemeId: 'f1',
    schemeName: 'PM Kisan Samman Nidhi',
    step: 1,
    title: 'Gather Required Documents',
    description: 'Collect Aadhaar card, land documents, and bank details. Get passport photo.',
    priority: 'high',
    estimatedTime: '1-2 days',
    status: 'pending'
  },
  {
    id: 'a5',
    schemeId: 'f1',
    schemeName: 'PM Kisan Samman Nidhi',
    step: 2,
    title: 'Visit Common Service Centre',
    description: 'Go to nearest CSC or Agriculture Office with documents for registration.',
    priority: 'high',
    estimatedTime: '2-3 hours',
    status: 'pending'
  },
  {
    id: 'a6',
    schemeId: 'f3',
    schemeName: 'Kisan Credit Card',
    step: 1,
    title: 'Apply at Bank',
    description: 'Visit your bank branch with land documents and apply for KCC.',
    priority: 'medium',
    estimatedTime: '2-3 hours',
    status: 'pending'
  }
];

export const mockReminders: Reminder[] = [
  {
    id: 'r1',
    title: 'NSP Scholarship Deadline',
    description: 'Complete your National Scholarship Portal application before deadline.',
    date: '2025-02-15',
    type: 'deadline',
    status: 'pending'
  },
  {
    id: 'r2',
    title: 'PM Kisan Registration',
    description: 'Complete registration for next installment cycle.',
    date: '2025-02-20',
    type: 'deadline',
    status: 'pending'
  },
  {
    id: 'r3',
    title: 'Income Certificate Follow-up',
    description: 'Check status of income certificate application at Tehsil office.',
    date: '2025-01-20',
    type: 'follow-up',
    status: 'pending'
  },
  {
    id: 'r4',
    title: 'Collect Passport Photos',
    description: 'Get passport-size photographs for scheme applications.',
    date: '2025-01-12',
    type: 'document',
    status: 'pending'
  }
];

export const defaultProfile: CitizenProfile = {
  fullName: '',
  age: 0,
  gender: 'male',
  dob: '',
  mobileNumber: '',
  email: '',
  address: '',
  state: '',
  district: '',
  pincode: '',
  incomeRange: '',
  occupation: 'Student',
  category: '',
  disability: false,
  familyStatus: 'Single',
  education: '',
  aadhaarNumber: '',
  bankAccountNumber: '',
  ifscCode: ''
};
