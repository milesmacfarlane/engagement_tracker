'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { useAuthStore } from '@/lib/auth-store';
import Link from 'next/link';

interface Student {
  student_id: string;
  name: string;
  primary_class: string;
}

interface ClassInfo {
  class_code: string;
  class_name: string;
}

export default function ReportsPage() {
  const { isAuthenticated } = useAuthStore();
  const [students, setStudents] = useState<Student[]>([]);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<'student' | 'class'>('student');
  const [selectedId, setSelectedId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isAuthenticated()) {
      loadData();
    }
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [studentRes, classRes] = await Promise.all([
        apiClient.listStudents(0, 1000),
        apiClient.listClasses(),
      ]);

      if (studentRes && studentRes.data) {
        setStudents(studentRes.data);
      }
      if (classRes) {
        setClasses(Array.isArray(classRes) ? classRes : classRes.data || []);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      setMessage({ type: 'error', text: 'Failed to load data' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedId) {
      setMessage({ type: 'error', text: 'Please select a student or class' });
      return;
    }

    try {
      setIsGenerating(true);
      const url = `http://localhost:8000/api/reports/${selectedReport}/${selectedId}?format=pdf`;

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      // Create blob and download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${selectedReport}_report_${selectedId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      setMessage({ type: 'success', text: 'Report generated successfully!' });
    } catch (error) {
      console.error('Error generating report:', error);
      setMessage({ type: 'error', text: 'Failed to generate report' });
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div>
        <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        </div>
        <div className="text-center py-12">
          <p className="text-gray-700">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Title Bar */}
      <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-700 mt-2">Generate and download PDF reports for students and classes</p>
      </div>

      {message && (
        <div
          className={`px-4 py-3 rounded mb-6 ${
            message.type === 'success'
              ? 'bg-green-600 border border-green-700 text-white'
              : 'bg-red-600 border border-red-700 text-white'
          }`}
        >
          {message.type === 'success' ? '✓' : '✗'} {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Student Reports */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Student Reports</h2>
          <p className="text-gray-700 mb-4">Generate a detailed performance report for a student.</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Student
              </label>
              <select
                value={selectedReport === 'student' ? selectedId : ''}
                onChange={(e) => {
                  setSelectedReport('student');
                  setSelectedId(e.target.value);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
              >
                <option value="">-- Choose a Student --</option>
                {students.map((s) => (
                  <option key={s.student_id} value={s.student_id}>
                    {s.name} ({s.student_id}) - {s.primary_class}
                  </option>
                ))}
              </select>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                <strong>Includes:</strong>
              </p>
              <ul className="text-sm text-gray-700 list-disc list-inside mt-2 space-y-1">
                <li>Student information and performance metrics</li>
                <li>Overall achievement percentage</li>
                <li>Performance band classification</li>
                <li>Detailed breakdown by engagement measure</li>
                <li>Attendance rate and observations count</li>
                <li>Recommended next steps for intervention</li>
              </ul>
            </div>

            <button
              onClick={() => {
                setSelectedReport('student');
                handleGenerateReport();
              }}
              disabled={isGenerating || (selectedReport === 'student' && !selectedId)}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg"
            >
              {isGenerating ? 'Generating...' : '📄 Generate Student Report (PDF)'}
            </button>
          </div>
        </div>

        {/* Class Reports */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Class Reports</h2>
          <p className="text-gray-700 mb-4">Generate a comprehensive report for an entire class.</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Class
              </label>
              <select
                value={selectedReport === 'class' ? selectedId : ''}
                onChange={(e) => {
                  setSelectedReport('class');
                  setSelectedId(e.target.value);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
              >
                <option value="">-- Choose a Class --</option>
                {classes.map((c) => (
                  <option key={c.class_code} value={c.class_code}>
                    {c.class_name} ({c.class_code})
                  </option>
                ))}
              </select>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                <strong>Includes:</strong>
              </p>
              <ul className="text-sm text-gray-700 list-disc list-inside mt-2 space-y-1">
                <li>Class information and overview</li>
                <li>Total student count and data availability</li>
                <li>Class average achievement percentage</li>
                <li>Class average attendance rate</li>
                <li>Performance distribution across bands</li>
                <li>Student rankings by achievement</li>
              </ul>
            </div>

            <button
              onClick={() => {
                setSelectedReport('class');
                handleGenerateReport();
              }}
              disabled={isGenerating || (selectedReport === 'class' && !selectedId)}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg"
            >
              {isGenerating ? 'Generating...' : '📊 Generate Class Report (PDF)'}
            </button>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Links</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/dashboard/students"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <p className="font-semibold text-gray-900">📋 View All Students</p>
            <p className="text-sm text-gray-600 mt-1">View student details and analytics</p>
          </Link>

          <Link
            href="/dashboard/classes"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <p className="font-semibold text-gray-900">📚 View All Classes</p>
            <p className="text-sm text-gray-600 mt-1">View class details and rankings</p>
          </Link>

          <Link
            href="/dashboard"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <p className="font-semibold text-gray-900">📊 Dashboard</p>
            <p className="text-sm text-gray-600 mt-1">Return to main dashboard overview</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
