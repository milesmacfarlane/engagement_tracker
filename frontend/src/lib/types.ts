/**
 * Core TypeScript types for the application
 */

// Authentication
export interface User {
  id: number;
  email: string;
  role: 'teacher' | 'admin';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  role?: 'teacher' | 'admin';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Students
export interface Student {
  student_id: string;
  name: string;
  primary_class: string;
}

export interface StudentListResponse {
  data: Student[];
  total: number;
  page: number;
  per_page: number;
}

// Classes
export interface Class {
  class_code: string;
  class_name: string;
}

export interface ClassDetail extends Class {
  student_count: number;
}

// Observations
export interface Observation {
  date: string;
  class_code: string;
  student_id: string;
  measure_name: string;
  value: '1' | '0' | '-';
}

export interface BatchObservationsRequest {
  observations: Observation[];
}

export interface ObservationListResponse {
  data: Observation[];
  total: number;
}

// Analytics
export interface MeasureStats {
  measure: string;
  performance_percentage: number | null;
  ones_observed: number;
  zeros_not_observed: number;
  not_applicable: number;
  band: string;
  status: string;
}

export interface StudentAnalytics {
  student_id: string;
  student_name: string;
  overall_performance: number | null;
  performance_band: string;
  performance_by_measure: MeasureStats[];
  attendance_rate: number | null;
  days_observed: number;
  days_absent: number;
  days_since_last_observation: number | null;
  recommended_next_steps: string;
}

export interface StudentSummary {
  student_id: string;
  student_name: string;
  achievement_percentage: number | null;
  attendance_percentage: number | null;
  band: string;
  status: string;
}

export interface ClassAnalytics {
  class_code: string;
  class_name: string;
  total_students: number;
  students_with_observations: number;
  average_performance: number | null;
  performance_distribution: Record<string, number>;
  student_summaries: StudentSummary[];
}

// API Error
export interface ApiError {
  detail: string;
}
