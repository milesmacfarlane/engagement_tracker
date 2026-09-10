/**
 * Dashboard Home Page
 */

'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { ClassAnalytics } from '@/lib/types';
import Link from 'next/link';

export default function DashboardPage() {
  const [classes, setClasses] = useState<ClassAnalytics[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      setIsLoading(true);
      const classList = await apiClient.listClasses();

      // Get analytics for each class
      const analyticsPromises = classList.map((c: any) =>
        apiClient.getClassAnalytics(c.class_code)
      );

      const analyticsData = await Promise.all(analyticsPromises);
      setClasses(analyticsData);
    } catch (error) {
      console.error('Failed to load classes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
      <p className="text-gray-600 mb-8">Overview of all classes and students</p>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading classes...</p>
        </div>
      ) : classes.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-700 mb-4">No classes found. Create one to get started.</p>
          <Link
            href="/classes"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Manage Classes
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes.map((classData) => (
            <Link
              key={classData.class_code}
              href={`/dashboard/class/${classData.class_code}`}
              className="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {classData.class_name}
              </h3>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Students:</span>
                  <span className="font-medium">{classData.total_students}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">With Observations:</span>
                  <span className="font-medium">{classData.students_with_observations}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Average Achievement:</span>
                  <span className="font-medium">
                    {classData.average_performance !== null
                      ? `${classData.average_performance.toFixed(1)}%`
                      : 'N/A'}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t">
                <p className="text-xs text-gray-500">Click to view class details</p>
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <Link
              href="/entry-log"
              className="block w-full text-left px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-900 rounded transition"
            >
              📝 Record Observations
            </Link>
            <Link
              href="/students"
              className="block w-full text-left px-4 py-2 bg-green-50 hover:bg-green-100 text-green-900 rounded transition"
            >
              👥 Manage Students
            </Link>
            <Link
              href="/classes"
              className="block w-full text-left px-4 py-2 bg-purple-50 hover:bg-purple-100 text-purple-900 rounded transition"
            >
              📚 Manage Classes
            </Link>
            <Link
              href="/reports"
              className="block w-full text-left px-4 py-2 bg-orange-50 hover:bg-orange-100 text-orange-900 rounded transition"
            >
              📄 View Reports
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>Total Classes: <span className="font-medium">{classes.length}</span></p>
            <p>Total Students: <span className="font-medium">
              {classes.reduce((sum, c) => sum + c.total_students, 0)}
            </span></p>
            <p>Students with Data: <span className="font-medium">
              {classes.reduce((sum, c) => sum + c.students_with_observations, 0)}
            </span></p>
          </div>
        </div>
      </div>
    </div>
  );
}
