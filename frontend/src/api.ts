import type {
  Course, CourseDetail, Department, ExtractionIssue,
  SemesterData
} from './types';

const API_BASE = 'http://localhost:8000/api/v1';

export const api = {
  // Academic
  async getDepartments(): Promise<Department[]> {
    const res = await fetch(`${API_BASE}/departments`);
    if (!res.ok) throw new Error('Failed to fetch departments');
    return res.json();
  },

  async getCourses(dept?: string, search?: string, limit = 50): Promise<Course[]> {
    const params = new URLSearchParams();
    if (dept) params.append('department_code', dept);
    if (search) params.append('search', search);
    params.append('limit', limit.toString());
    const res = await fetch(`${API_BASE}/courses?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch courses');
    return res.json();
  },

  async getCourseDetail(courseId: number): Promise<CourseDetail> {
    const res = await fetch(`${API_BASE}/courses/${courseId}`);
    if (!res.ok) throw new Error('Failed to fetch course details');
    return res.json();
  },

  async getSemester(deptCode: string, semNum: number): Promise<SemesterData> {
    const res = await fetch(`${API_BASE}/semesters?department_code=${deptCode}&semester_number=${semNum}`);
    if (!res.ok) throw new Error('Failed to fetch semester data');
    return res.json();
  },

  // Chat
  async sendChat(query: string, sessionId?: string, deptCode?: string, langPref?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        department_code: deptCode,
        language_preference: langPref
      })
    });
    if (!res.ok) throw new Error('Failed to send chat message');
    return res.json();
  },

  async submitFeedback(sessionId?: string, rating = 5, comments?: string): Promise<any> {
    const res = await fetch(`${API_BASE}/chat/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, rating, comments })
    });
    return res.json();
  },


  // Auth & Admin
  async login(username: string, password: string): Promise<any> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error('Invalid credentials');
    return res.json();
  },

  async getExtractionIssues(): Promise<ExtractionIssue[]> {
    const res = await fetch(`${API_BASE}/admin/extraction-issues`);
    if (!res.ok) throw new Error('Failed to fetch extraction issues');
    return res.json();
  },

  async updateExtractionIssue(id: number, status: string, notes: string, token: string): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/extraction-issues/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ status, resolution_notes: notes })
    });
    if (!res.ok) throw new Error('Failed to update issue');
    return res.json();
  },

  async getEvaluations(): Promise<any> {
    const res = await fetch(`${API_BASE}/admin/evaluations`);
    if (!res.ok) throw new Error('Failed to fetch evaluations');
    return res.json();
  },

  getSourcePageImageUrl(docId: string, pageNum: number): string {
    return `${API_BASE}/sources/${docId}/page/${pageNum}?format=image`;
  }
};
