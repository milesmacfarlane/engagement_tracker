/**
 * API Client - Axios instance with automatic token management
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { AuthResponse, User } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private instance: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.instance = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add token to headers
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid - clear and redirect to login
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  getToken(): string | null {
    return this.token;
  }

  loadToken() {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('auth_token');
      if (stored) {
        this.token = stored;
      }
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  }

  // Auth
  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await this.instance.post<AuthResponse>('/auth/register', {
      email,
      password,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.instance.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    await this.instance.post('/auth/logout');
    this.clearToken();
  }

  // Students
  async listStudents(page: number = 0, limit: number = 10, classCode?: string) {
    const params = new URLSearchParams({
      skip: String(page * limit),
      limit: String(limit),
    });
    if (classCode) params.append('class_code', classCode);

    const response = await this.instance.get('/students', { params });
    return response.data;
  }

  async getStudent(studentId: string) {
    const response = await this.instance.get(`/students/${studentId}`);
    return response.data;
  }

  async createStudent(studentId: string, name: string, primaryClass: string) {
    const response = await this.instance.post('/students', {
      student_id: studentId,
      name,
      primary_class: primaryClass,
    });
    return response.data;
  }

  async updateStudent(studentId: string, name: string, primaryClass: string) {
    const response = await this.instance.put(`/students/${studentId}`, {
      student_id: studentId,
      name,
      primary_class: primaryClass,
    });
    return response.data;
  }

  async deleteStudent(studentId: string) {
    await this.instance.delete(`/students/${studentId}`);
  }

  async bulkImportStudents(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.instance.post('/students/bulk-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Classes
  async listClasses() {
    const response = await this.instance.get('/classes');
    return response.data;
  }

  async getClass(classCode: string) {
    const response = await this.instance.get(`/classes/${classCode}`);
    return response.data;
  }

  async createClass(classCode: string, className: string) {
    const response = await this.instance.post('/classes', {
      class_code: classCode,
      class_name: className,
    });
    return response.data;
  }

  async updateClass(classCode: string, className: string) {
    const response = await this.instance.put(`/classes/${classCode}`, {
      class_code: classCode,
      class_name: className,
    });
    return response.data;
  }

  async deleteClass(classCode: string) {
    await this.instance.delete(`/classes/${classCode}`);
  }

  // Observations
  async listObservations(dateFilter?: string, classCode?: string, studentId?: string) {
    const params = new URLSearchParams();
    if (dateFilter) params.append('date_filter', dateFilter);
    if (classCode) params.append('class_code', classCode);
    if (studentId) params.append('student_id', studentId);

    const response = await this.instance.get('/observations', { params });
    return response.data;
  }

  async batchSaveObservations(observations: any[]) {
    const response = await this.instance.post('/observations/batch', {
      observations,
    });
    return response.data;
  }

  async exportObservations(dateFilter?: string, classCode?: string) {
    const params = new URLSearchParams();
    if (dateFilter) params.append('date_filter', dateFilter);
    if (classCode) params.append('class_code', classCode);

    const response = await this.instance.get('/observations/export', {
      params,
      responseType: 'blob',
    });

    return response.data;
  }

  // Analytics
  async getStudentAnalytics(studentId: string) {
    const response = await this.instance.get(`/analytics/student/${studentId}`);
    return response.data;
  }

  async getClassAnalytics(classCode: string) {
    const response = await this.instance.get(`/analytics/class/${classCode}`);
    return response.data;
  }

  // Reports
  async getStudentReport(studentId: string, format: 'pdf' | 'html' = 'html') {
    if (format === 'pdf') {
      const response = await this.instance.get(`/reports/student/${studentId}`, {
        params: { format },
        responseType: 'blob',
      });
      return response.data;
    }

    const response = await this.instance.get(`/reports/student/${studentId}`, {
      params: { format },
    });
    return response.data;
  }

  async getClassReport(classCode: string, format: 'pdf' | 'html' = 'html') {
    const response = await this.instance.get(`/reports/class/${classCode}`, {
      params: { format },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
