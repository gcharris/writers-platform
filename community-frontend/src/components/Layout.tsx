import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { UserCircleIcon, ArrowRightOnRectangleIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold text-sky-600">
                Writers Community
              </Link>
              <nav className="hidden md:flex gap-6">
                <Link
                  to="/browse"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Browse
                </Link>
                <a
                  href="https://writersfactory.app"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Factory
                </a>
              </nav>
            </div>

            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/upload"
                    className="hidden sm:inline-flex items-center gap-2 px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm font-medium"
                  >
                    <ArrowUpTrayIcon className="h-4 w-4" />
                    Upload
                  </Link>
                  <div className="flex items-center gap-2 text-gray-700">
                    <UserCircleIcon className="h-5 w-5" />
                    <span className="text-sm font-medium hidden sm:inline">{user?.username}</span>
                  </div>
                  <button
                    onClick={() => {
                      logout();
                      window.location.href = '/';
                    }}
                    className="inline-flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors text-sm"
                  >
                    <ArrowRightOnRectangleIcon className="h-5 w-5" />
                    <span className="hidden sm:inline">Logout</span>
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors text-sm font-medium"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main>{children}</main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Writers Community</h3>
              <p className="text-sm text-gray-600">
                Discover AI-validated fiction and share your own work with readers
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Platform</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/browse" className="text-gray-600 hover:text-gray-900">
                    Browse Works
                  </Link>
                </li>
                <li>
                  <Link to="/upload" className="text-gray-600 hover:text-gray-900">
                    Upload Your Work
                  </Link>
                </li>
                <li>
                  <a
                    href="https://writersfactory.app"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-gray-900"
                  >
                    Writers Factory →
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-3">About</h3>
              <p className="text-sm text-gray-600">
                Part of the Writers Platform ecosystem, bringing transparency to AI-assisted writing.
              </p>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm text-gray-500">
            © 2025 Writers Platform. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
