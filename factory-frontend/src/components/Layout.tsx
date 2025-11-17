import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      {isAuthenticated && (
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-8">
                <Link to="/dashboard" className="text-xl font-bold text-indigo-600">
                  Writers Factory
                </Link>
                <nav className="hidden md:flex gap-6">
                  <Link
                    to="/dashboard"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Dashboard
                  </Link>
                  <a
                    href="https://writerscommunity.app"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    Community
                  </a>
                </nav>
              </div>

              <div className="flex items-center gap-4">
                {user && (
                  <div className="flex items-center gap-2 text-gray-700">
                    <UserCircleIcon className="h-5 w-5" />
                    <span className="text-sm font-medium">{user.username}</span>
                  </div>
                )}
                <button
                  onClick={() => {
                    logout();
                    window.location.href = '/login';
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                  <span className="text-sm">Logout</span>
                </button>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Main content */}
      <main>{children}</main>
    </div>
  );
}
