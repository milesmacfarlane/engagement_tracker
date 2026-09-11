/**
 * Classes Management Page
 */

'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { Class } from '@/lib/types';

export default function ClassesPage() {
  const [classes, setClasses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingCode, setEditingCode] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    class_code: '',
    class_name: '',
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      setIsLoading(true);
      const res = await apiClient.listClasses();
      setClasses(res);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load classes' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.class_code || !formData.class_name) {
      setMessage({ type: 'error', text: 'All fields are required' });
      return;
    }

    try {
      if (editingCode) {
        await apiClient.updateClass(editingCode, formData.class_name);
        setMessage({ type: 'success', text: 'Class updated' });
      } else {
        await apiClient.createClass(formData.class_code, formData.class_name);
        setMessage({ type: 'success', text: 'Class created' });
      }
      await loadClasses();
      setShowForm(false);
      setFormData({ class_code: '', class_name: '' });
      setEditingCode(null);
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Operation failed';
      setMessage({ type: 'error', text: msg });
    }
  };

  const handleDelete = async (code: string) => {
    if (!confirm('Delete this class?')) return;
    try {
      await apiClient.deleteClass(code);
      setMessage({ type: 'success', text: 'Class deleted' });
      await loadClasses();
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Failed to delete';
      setMessage({ type: 'error', text: msg });
    }
  };

  const handleEdit = (cls: any) => {
    setFormData({
      class_code: cls.class_code,
      class_name: cls.class_name,
    });
    setEditingCode(cls.class_code);
    setShowForm(true);
  };

  return (
    <div>
      {/* Breadcrumb */}
      <div className="text-sm text-gray-600 mb-4">
        <a href="/dashboard" className="hover:text-blue-600">Dashboard</a> / <span className="text-gray-900">Classes</span>
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">Classes</h1>
      <p className="text-gray-600 mb-6">Manage classes and sections. Create classes first, then add students.</p>

      {message && (
        <div
          className={`px-4 py-3 rounded mb-6 ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          {message.type === 'success' ? '✓' : '✗'} {message.text}
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {editingCode ? 'Edit Class' : 'Add Class'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Class Code
              </label>
              <input
                type="text"
                value={formData.class_code}
                onChange={(e) => setFormData({ ...formData, class_code: e.target.value })}
                disabled={!!editingCode}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., HIS20A"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Class Name
              </label>
              <input
                type="text"
                value={formData.class_name}
                onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., History 20 Section A"
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
              >
                {editingCode ? 'Update' : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingCode(null);
                  setFormData({ class_code: '', class_name: '' });
                }}
                className="px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="text-center text-gray-500 col-span-full py-12">Loading...</div>
        ) : classes.length === 0 ? (
          <div className="col-span-full">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
              <p className="text-gray-600 mb-4">No classes yet. Create your first class to get started.</p>
              <button
                onClick={() => setShowForm(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
              >
                Create First Class
              </button>
            </div>
          </div>
        ) : (
          classes.map((cls) => (
            <div key={cls.class_code} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {cls.class_name}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Code: <span className="font-mono font-medium">{cls.class_code}</span>
              </p>
              {cls.student_count && (
                <p className="text-sm text-gray-600 mb-4">
                  Students: <span className="font-medium">{cls.student_count}</span>
                </p>
              )}
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(cls)}
                  className="flex-1 text-blue-600 hover:text-blue-700 font-medium text-sm py-1"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(cls.class_code)}
                  className="flex-1 text-red-600 hover:text-red-700 font-medium text-sm py-1"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {!showForm && classes.length > 0 && (
        <div className="mt-8 flex gap-4">
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
          >
            Add Class
          </button>
          <a
            href="/students"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium inline-block"
          >
            Next: Add Students →
          </a>
        </div>
      )}
    </div>
  );
}
