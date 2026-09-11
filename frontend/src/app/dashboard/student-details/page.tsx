'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useAuthStore } from '@/lib/auth-store';
import Link from 'next/link';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface MeasureStats {
  measure: string;
  performance_percentage: number | null;
  ones_observed: number;
  zeros_not_observed: number;
  not_applicable: number;
  band: string;
  status: string;
}

interface StudentAnalytics {
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

export default function StudentDetailsPage() {
  const { isAuthenticated } = useAuthStore();
  const searchParams = useSearchParams();
  const studentId = searchParams.get('id');
  const [data, setData] = useState<StudentAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!studentId || !isAuthenticated()) return;

    const loadData = async () => {
      try {
        setIsLoading(true);
        const response = await apiClient.getStudentAnalytics(studentId);
        setData(response);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load student analytics');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [studentId, isAuthenticated()]);

  if (!studentId) {
    return (
      <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Student Details</h1>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div>
        <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Student Details</h1>
        </div>
        <div className="text-center py-12">
          <p className="text-gray-700">Loading student data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div>
        <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Student Details</h1>
        </div>
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded">
          {error || 'Failed to load student data'}
        </div>
        <div className="mt-4">
          <Link href="/dashboard/students" className="text-blue-600 hover:text-blue-700">
            ← Back to Students
          </Link>
        </div>
      </div>
    );
  }

  const getBandColor = (band: string) => {
    switch (band) {
      case 'Exemplary':
        return 'bg-green-100 text-green-900 border border-green-300';
      case 'Proficient':
        return 'bg-blue-100 text-blue-900 border border-blue-300';
      case 'Developing':
        return 'bg-yellow-100 text-yellow-900 border border-yellow-300';
      case 'Emerging':
        return 'bg-orange-100 text-orange-900 border border-orange-300';
      default:
        return 'bg-red-100 text-red-900 border border-red-300';
    }
  };

  return (
    <div>
      {/* Shaded Title Bar */}
      <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
        <Link href="/dashboard/students" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
          ← Back to Students
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{data.student_name}</h1>
        <p className="text-gray-700">Student ID: {data.student_id}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Achievement %</p>
          <p className="text-3xl font-bold text-gray-900">
            {data.overall_performance !== null ? `${data.overall_performance.toFixed(1)}%` : 'N/A'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Performance Band</p>
          <div className={`inline-block px-3 py-1 rounded-full font-semibold text-sm mt-2 ${getBandColor(data.performance_band)}`}>
            {data.performance_band}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Attendance</p>
          <p className="text-3xl font-bold text-gray-900">
            {data.attendance_rate !== null ? `${data.attendance_rate.toFixed(1)}%` : 'N/A'}
          </p>
          <p className="text-xs text-gray-600 mt-1">{data.days_observed} days observed, {data.days_absent} absent</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Last Observation</p>
          <p className="text-lg font-bold text-gray-900">
            {data.days_since_last_observation !== null ? `${data.days_since_last_observation} days ago` : 'Never'}
          </p>
        </div>
      </div>

      {/* Performance Chart by Measure */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Performance by Measure</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data.performance_by_measure}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="measure"
              angle={-45}
              textAnchor="end"
              height={100}
              tick={{ fontSize: 12 }}
            />
            <YAxis domain={[0, 100]} label={{ value: 'Performance %', angle: -90, position: 'insideLeft' }} />
            <Tooltip
              formatter={(value) => `${typeof value === 'number' ? value.toFixed(1) : value}%`}
              labelFormatter={(label) => `Measure: ${label}`}
            />
            <Bar dataKey="performance_percentage" fill="#3b82f6" name="Performance %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Performance by Measure Details */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Detailed Measure Breakdown</h2>
        <div className="space-y-4">
          {data.performance_by_measure.map((measure) => (
            <div key={measure.measure} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-gray-900">{measure.measure}</h3>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">
                    {measure.performance_percentage !== null ? `${measure.performance_percentage.toFixed(1)}%` : 'N/A'}
                  </p>
                  <div className={`inline-block px-2 py-1 rounded text-xs font-semibold mt-1 ${getBandColor(measure.band)}`}>
                    {measure.band}
                  </div>
                </div>
              </div>
              <div className="flex gap-4 text-sm text-gray-600">
                <span>✓ Observed: {measure.ones_observed}</span>
                <span>✗ Not Observed: {measure.zeros_not_observed}</span>
                <span>- N/A: {measure.not_applicable}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Next Steps */}
      {data.recommended_next_steps && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-3">📋 Recommended Next Steps</h2>
          <p className="text-gray-900">{data.recommended_next_steps}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Link
          href="/dashboard/students"
          className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium inline-block"
        >
          Back to Students
        </Link>
      </div>
    </div>
  );
}
