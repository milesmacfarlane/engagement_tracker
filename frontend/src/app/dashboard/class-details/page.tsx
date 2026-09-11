'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useAuthStore } from '@/lib/auth-store';
import Link from 'next/link';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface StudentSummary {
  student_id: string;
  student_name: string;
  achievement_percentage: number | null;
  attendance_percentage: number | null;
  band: string;
  status: string;
}

interface ClassAnalytics {
  class_code: string;
  class_name: string;
  total_students: number;
  students_with_observations: number;
  average_performance: number | null;
  performance_distribution: Record<string, number>;
  student_summaries: StudentSummary[];
}

export default function ClassDetailsPage() {
  const { isAuthenticated } = useAuthStore();
  const searchParams = useSearchParams();
  const classCode = searchParams.get('code');
  const [data, setData] = useState<ClassAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!classCode || !isAuthenticated()) return;

    const loadData = async () => {
      try {
        setIsLoading(true);
        const response = await apiClient.getClassAnalytics(classCode);
        setData(response);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load class analytics');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [classCode, isAuthenticated()]);

  if (!classCode) {
    return <div>Missing class code</div>;
  }

  if (isLoading) {
    return (
      <div>
        <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Class Details</h1>
        </div>
        <div className="text-center py-12">
          <p className="text-gray-700">Loading class data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div>
        <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Class Details</h1>
        </div>
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded">
          {error || 'Failed to load class data'}
        </div>
      </div>
    );
  }

  const getBandColor = (band: string) => {
    switch (band) {
      case 'Exemplary':
        return 'bg-green-100 text-green-900';
      case 'Proficient':
        return 'bg-blue-100 text-blue-900';
      case 'Developing':
        return 'bg-yellow-100 text-yellow-900';
      case 'Emerging':
        return 'bg-orange-100 text-orange-900';
      default:
        return 'bg-red-100 text-red-900';
    }
  };

  const getStatusColor = (status: string) => {
    if (status.includes('✓')) return 'text-green-700';
    if (status.includes('🔴')) return 'text-red-700';
    if (status.includes('⚠️')) return 'text-orange-700';
    return 'text-gray-700';
  };

  return (
    <div>
      {/* Shaded Title Bar */}
      <div className="bg-gray-100 -mx-8 -mt-8 px-8 py-6 mb-8">
        <Link href="/dashboard" className="text-blue-600 hover:text-blue-700 text-sm mb-2 inline-block">
          ← Back to Dashboard
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{data.class_name}</h1>
        <p className="text-gray-700">Class Code: {data.class_code}</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Total Students</p>
          <p className="text-3xl font-bold text-gray-900">{data.total_students}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">With Observations</p>
          <p className="text-3xl font-bold text-gray-900">{data.students_with_observations}</p>
          <p className="text-xs text-gray-600 mt-1">
            {data.total_students > 0 ? `${((data.students_with_observations / data.total_students) * 100).toFixed(0)}%` : '0%'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-1">Class Average</p>
          <p className="text-3xl font-bold text-gray-900">
            {data.average_performance !== null ? `${data.average_performance.toFixed(1)}%` : 'N/A'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm text-gray-700 mb-2">Performance Distribution</p>
          <div className="space-y-1 text-xs">
            {Object.entries(data.performance_distribution)
              .filter(([_, count]) => count > 0)
              .map(([band, count]) => (
                <div key={band} className="flex justify-between">
                  <span>{band}:</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Performance Distribution Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Performance Band Distribution</h2>
        <div className="flex justify-center">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(data.performance_distribution)
                  .filter(([_, count]) => count > 0)
                  .map(([band, count]) => ({ name: band, value: count }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                <Cell fill="#10b981" />
                <Cell fill="#3b82f6" />
                <Cell fill="#f59e0b" />
                <Cell fill="#ef6b3d" />
                <Cell fill="#ef4444" />
                <Cell fill="#991b1b" />
              </Pie>
              <Tooltip formatter={(value) => `${value} students`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Student Performance Table */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Student Performance Rankings</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Student Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Achievement %</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Band</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Attendance %</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.student_summaries
                .sort((a, b) => {
                  const aPerf = a.achievement_percentage ?? -1;
                  const bPerf = b.achievement_percentage ?? -1;
                  return bPerf - aPerf;
                })
                .map((student) => (
                  <tr key={student.student_id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 text-sm text-gray-900 font-medium">{student.student_name}</td>
                    <td className="px-6 py-3 text-sm text-gray-900">
                      {student.achievement_percentage !== null ? `${student.achievement_percentage.toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getBandColor(student.band)}`}>
                        {student.band}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-900">
                      {student.attendance_percentage !== null ? `${student.attendance_percentage.toFixed(1)}%` : 'N/A'}
                    </td>
                    <td className={`px-6 py-3 text-sm font-medium ${getStatusColor(student.status)}`}>
                      {student.status}
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <Link
                        href={`/dashboard/student-details?id=${student.student_id}`}
                        className="text-blue-600 hover:text-blue-700 font-medium"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-4">
        <Link
          href="/dashboard"
          className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium inline-block"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
