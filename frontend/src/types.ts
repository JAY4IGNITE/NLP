export interface Department {
  id: number;
  code: string;
  name: string;
  vision?: string;
  mission?: string;
}

export interface Course {
  id: number;
  code: string;
  title: string;
  department_code?: string;
  category?: string;
  level?: string;
  credits: number;
  lecture_hours: number;
  tutorial_hours: number;
  practical_hours: number;
  total_hours: number;
  prerequisite_text?: string;
  source_document_id?: string;
  source_page?: number;
}

export interface CourseUnit {
  unit_number: number;
  unit_roman: string;
  title?: string;
  content: string;
  practice_content?: string;
  source_page?: number;
}

export interface CourseOutcome {
  outcome_code: string;
  description: string;
}

export interface Textbook {
  book_type: string;
  title: string;
  raw_text?: string;
}

export interface CourseDetail extends Course {
  units: CourseUnit[];
  outcomes: CourseOutcome[];
  textbooks: Textbook[];
}

export interface SemesterCourse {
  code: string;
  title: string;
  category: string;
  credits: number;
  level?: string;
  lecture_hours: number;
  tutorial_hours: number;
  practical_hours: number;
  total_hours: number;
  is_elective: boolean;
  source_page?: number;
}

export interface SemesterData {
  department: string;
  department_code: string;
  semester_number: number;
  semester_roman: string;
  total_credits: number;
  total_courses: number;
  courses: SemesterCourse[];
  source_page?: number;
}

export interface Citation {
  doc_id: string;
  title: string;
  department: string;
  page: number;
  excerpt: string;
  course_code?: string;
  score?: number;
}

export interface ChatMessageItem {
  id?: number | string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  domain?: string;
  confidence?: number;
  error?: boolean;
  citations?: Citation[];
  source_type?: string;
  is_grounded?: boolean;
  created_at?: string;
  thinkingDuration?: number;
  thinkingSteps?: string[];
}

export interface ExtractionIssue {
  id: number;
  doc_id: string;
  course_code?: string;
  issue_type: string;
  severity: string;
  details?: any;
  status: string;
  created_at?: string;
}
