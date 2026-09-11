/**
 * Protected Route - Redirects to login if not authenticated
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token } = useAuthStore();

  useEffect(() => {
    // Initialize auth on mount
    useAuthStore.getState().initialize();
  }, []);

  useEffect(() => {
    // Check if authenticated after initialization
    const checkAuth = async () => {
      const { token: currentToken } = useAuthStore.getState();
      if (!currentToken) {
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  // Show loading until we know auth status
  if (!token) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return <>{children}</>;
}
