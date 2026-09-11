/**
 * Sidebar Navigation Component
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { useAuthStore } from '@/lib/auth-store';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/dashboard/entry-log', label: 'Quick Entry Log', icon: '📝' },
  { href: '/dashboard/students', label: 'Students', icon: '👥' },
  { href: '/dashboard/classes', label: 'Classes', icon: '📚' },
  { href: '/dashboard/reports', label: 'Reports', icon: '📄' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuthStore();
  const [isOpen, setIsOpen] = useState(true);

  return (
    <aside
      className={`${
        isOpen ? 'w-64' : 'w-20'
      } bg-gradient-to-b from-blue-900 to-blue-800 text-white transition-all duration-300 flex flex-col`}
    >
      {/* Header */}
      <div className="p-4 border-b border-blue-700">
        {isOpen && (
          <div>
            <h1 className="text-xl font-bold">Engagement</h1>
            <p className="text-xs text-blue-200">Tracker</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-blue-100 hover:bg-blue-700'
              }`}
              title={item.label}
            >
              <span className="text-lg">{item.icon}</span>
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User & Logout */}
      <div className="p-4 border-t border-blue-700 space-y-3">
        {isOpen && user && (
          <div className="text-xs text-blue-200 truncate">
            <p className="font-semibold truncate">{user.email}</p>
            <p className="text-blue-300 capitalize">{user.role}</p>
          </div>
        )}
        <button
          onClick={() => logout()}
          className="w-full text-left px-3 py-2 text-sm text-blue-100 hover:bg-blue-700 rounded transition"
        >
          {isOpen ? 'Sign Out' : '→'}
        </button>
      </div>

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-blue-700 transition"
        title={isOpen ? 'Collapse' : 'Expand'}
      >
        <span className="text-lg">{isOpen ? '←' : '→'}</span>
      </button>
    </aside>
  );
}
