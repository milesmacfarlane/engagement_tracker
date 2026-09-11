/**
 * Entry Log Page - Quick observation entry with keyboard navigation
 */

'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { useEntryLogKeyboard } from '@/hooks/use-entry-log-keyboard';
import { Student, Observation } from '@/lib/types';

const MEASURES = [
  'Time on Task',
  'Asked/Answered/Shared',
  'Engaged with Content and Others',
  'Materials/Organized',
  'Seeks Teacher Support',
];

interface GridData {
  studentId: string;
  studentName: string;
  values: Record<string, string>;
}

export default function EntryLogPage() {
  const [classes, setClasses] = useState<any[]>([]);
  const [selectedClass, setSelectedClass] = useState<string>('');
  const [observationDate, setObservationDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [students, setStudents] = useState<Student[]>([]);
  const [gridData, setGridData] = useState<GridData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Grid data for keyboard navigation
  const gridArray = gridData.map((row) =>
    MEASURES.map((measure) => row.values[measure] || '')
  );

  const { handleKeyDown, setInputRef, focusCell } = useEntryLogKeyboard(
    gridArray,
    (row, col, value) => {
      const measure = MEASURES[col];
      const newGridData = [...gridData];
      newGridData[row].values[measure] = value;
      setGridData(newGridData);
    },
    () => handleSave()
  );

  // Load classes on mount
  useEffect(() => {
    loadClasses();
  }, []);

  // Load students when class changes
  useEffect(() => {
    if (selectedClass) {
      loadStudents();
    }
  }, [selectedClass]);

  const loadClasses = async () => {
    try {
      const classList = await apiClient.listClasses();
      setClasses(classList);
      if (classList.length > 0) {
        setSelectedClass(classList[0].class_code);
      }
    } catch (error) {
      console.error('Failed to load classes:', error);
    }
  };

  const loadStudents = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.listStudents(0, 100, selectedClass);
      const studentList = response.data;
      setStudents(studentList);

      // Initialize grid data
      const initialGridData = studentList.map((student: Student) => ({
        studentId: student.student_id,
        studentName: student.name,
        values: {} as Record<string, string>,
      }));
      setGridData(initialGridData);
    } catch (error) {
      console.error('Failed to load students:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAbsentClick = (rowIndex: number) => {
    // Mark all cells in row as '0'
    const newGridData = [...gridData];
    MEASURES.forEach((measure) => {
      newGridData[rowIndex].values[measure] = '0';
    });
    setGridData(newGridData);
  };

  const handleClearRow = (rowIndex: number) => {
    const newGridData = [...gridData];
    MEASURES.forEach((measure) => {
      newGridData[rowIndex].values[measure] = '';
    });
    setGridData(newGridData);
  };

  const handleSave = async () => {
    setSaveMessage(null);
    setSaveError(null);

    if (!selectedClass || gridData.length === 0) {
      setSaveError('Please select a class');
      return;
    }

    try {
      setIsSaving(true);

      // Build observations array
      const observations: Observation[] = [];
      gridData.forEach((row) => {
        MEASURES.forEach((measure) => {
          const value = row.values[measure];
          if (value) {
            observations.push({
              date: observationDate,
              class_code: selectedClass,
              student_id: row.studentId,
              measure_name: measure,
              value: value as '1' | '0' | '-',
            });
          }
        });
      });

      if (observations.length === 0) {
        setSaveError('No observations to save');
        return;
      }

      await apiClient.batchSaveObservations(observations);
      setSaveMessage(`Saved ${observations.length} observations`);

      // Clear grid
      const newGridData = gridData.map((row) => ({
        ...row,
        values: {},
      }));
      setGridData(newGridData);

      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to save observations';
      setSaveError(message);
    } finally {
      setIsSaving(false);
    }
  };

  const absentCount = gridData.filter(
    (row) =>
      Object.values(row.values).length > 0 &&
      Object.values(row.values).every((v) => v === '0')
  ).length;

  const filledCount = gridData.filter(
    (row) => Object.values(row.values).length > 0
  ).length;

  return (
    <div>
      {/* Breadcrumb */}
      <div className="text-sm text-gray-900 mb-4">
        <a href="/dashboard" className="hover:text-blue-600">Dashboard</a> / <span className="text-gray-900">Quick Entry Log</span>
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-2">Quick Entry Log</h1>
      <p className="text-gray-900 mb-6">
        Record observations using keyboard shortcuts: press 1, 0, or - for each behavior
      </p>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observation Date
            </label>
            <input
              type="date"
              value={observationDate}
              onChange={(e) => setObservationDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Class
            </label>
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
            >
              <option value="">Select a class</option>
              {classes.map((c) => (
                <option key={c.class_code} value={c.class_code}>
                  {c.class_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Progress
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-600 transition-all"
                  style={{
                    width: `${gridData.length > 0 ? (filledCount / gridData.length) * 100 : 0}%`,
                  }}
                />
              </div>
              <span className="text-sm text-gray-900">
                {filledCount}/{gridData.length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      {saveMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-6">
          ✓ {saveMessage}
        </div>
      )}

      {saveError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          ✗ {saveError}
        </div>
      )}

      {/* Grid */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-700">Loading students...</p>
        </div>
      ) : gridData.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-700">Select a class to begin recording observations</p>
        </div>
      ) : (
        <div>
          {/* Desktop Grid */}
          <div className="hidden md:block bg-white rounded-lg shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b">
                  <th className="px-4 py-3 text-left font-semibold text-gray-900 sticky left-0 z-10 bg-gray-50">
                    Student
                  </th>
                  {MEASURES.map((measure) => (
                    <th
                      key={measure}
                      className="px-2 py-3 text-center font-semibold text-gray-900 whitespace-nowrap"
                      title={measure}
                    >
                      <div className="text-xs">{measure.substring(0, 10)}</div>
                    </th>
                  ))}
                  <th className="px-4 py-3 text-center font-semibold text-gray-900">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {gridData.map((row, rowIndex) => (
                  <tr key={row.studentId} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900 sticky left-0 z-10 bg-white">
                      {row.studentName}
                    </td>
                    {MEASURES.map((measure, colIndex) => (
                      <td key={measure} className="px-2 py-3 text-center">
                        <input
                          type="text"
                          ref={(el) => setInputRef(rowIndex, colIndex, el)}
                          value={row.values[measure] || ''}
                          onChange={(e) => {
                            const value = e.target.value.slice(-1);
                            if (['1', '0', '-', ''].includes(value)) {
                              const newGridData = [...gridData];
                              newGridData[rowIndex].values[measure] = value;
                              setGridData(newGridData);
                            }
                          }}
                          onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex)}
                          maxLength={1}
                          className="w-8 h-8 text-center border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent font-semibold"
                          placeholder="-"
                        />
                      </td>
                    ))}
                    <td className="px-4 py-3 text-center space-x-2">
                      <button
                        onClick={() => handleAbsentClick(rowIndex)}
                        className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded"
                        title="Mark all as absent (0)"
                      >
                        Absent
                      </button>
                      <button
                        onClick={() => handleClearRow(rowIndex)}
                        className="px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 rounded"
                        title="Clear row"
                      >
                        Clear
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Summary */}
          <div className="mt-6 bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-900">Total Students</p>
                <p className="text-2xl font-bold text-gray-900">{gridData.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-900">Recorded</p>
                <p className="text-2xl font-bold text-blue-600">{filledCount}</p>
              </div>
              <div>
                <p className="text-sm text-gray-900">Absent</p>
                <p className="text-2xl font-bold text-orange-600">{absentCount}</p>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSave}
              disabled={isSaving || filledCount === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              {isSaving ? 'Saving...' : `Save Observations (${filledCount})`}
            </button>
            <button
              onClick={() => {
                const newGridData = gridData.map((row) => ({
                  ...row,
                  values: {},
                }));
                setGridData(newGridData);
              }}
              className="px-6 py-3 border border-gray-300 hover:bg-gray-50 rounded-lg font-semibold transition"
            >
              Clear All
            </button>
          </div>

          {/* Keyboard Help */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">⌨️ Keyboard Shortcuts</h3>
            <div className="grid grid-cols-2 gap-4 text-sm text-blue-800">
              <div>
                <p><strong>1</strong> - Observed</p>
                <p><strong>0</strong> - Not Observed</p>
                <p><strong>-</strong> - N/A</p>
              </div>
              <div>
                <p><strong>Tab</strong> - Next cell</p>
                <p><strong>Arrow Keys</strong> - Navigate</p>
                <p><strong>Enter</strong> - Next/Save</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
