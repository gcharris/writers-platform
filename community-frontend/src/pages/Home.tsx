import { Link } from 'react-router-dom';
import { BadgeExplainer } from '../components/Badge';
import { BookOpenIcon, ArrowUpTrayIcon, SparklesIcon } from '@heroicons/react/24/outline';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-sky-50 via-white to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6">
              Discover AI-Validated Fiction
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Browse manuscripts developed with professional AI analysis. Every work tells you how it was crafted.
            </p>
            <Link
              to="/browse"
              className="inline-flex items-center px-8 py-4 bg-sky-600 text-white text-lg font-medium rounded-lg hover:bg-sky-700 transition-colors"
            >
              <BookOpenIcon className="h-6 w-6 mr-2" />
              Start Reading
            </Link>
          </div>
        </div>
      </div>

      {/* Badge Explainer */}
      <BadgeExplainer />

      {/* CTA Section */}
      <div className="bg-white py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-sky-600 to-blue-600 rounded-2xl shadow-xl overflow-hidden">
            <div className="px-8 py-12 sm:px-12 sm:py-16">
              <h2 className="text-3xl font-bold text-white mb-4">
                Ready to Share Your Work?
              </h2>
              <p className="text-sky-100 text-lg mb-8">
                Join our community of writers and get your work in front of readers
              </p>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Upload to Community */}
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                  <ArrowUpTrayIcon className="h-10 w-10 text-white mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Upload to Community
                  </h3>
                  <p className="text-sky-100 mb-4">
                    Share your work directly with readers. Optional AI verification available.
                  </p>
                  <Link
                    to="/upload"
                    className="inline-block px-6 py-3 bg-white text-sky-600 font-medium rounded-lg hover:bg-sky-50 transition-colors"
                  >
                    Upload Now
                  </Link>
                </div>

                {/* Get AI Feedback */}
                <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
                  <SparklesIcon className="h-10 w-10 text-white mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">
                    Get AI Feedback First
                  </h3>
                  <p className="text-sky-100 mb-4">
                    Refine your work with multi-model AI analysis before publishing.
                  </p>
                  <a
                    href="https://writersfactory.app"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block px-6 py-3 bg-white text-sky-600 font-medium rounded-lg hover:bg-sky-50 transition-colors"
                  >
                    Try Writers Factory →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">
            Why Writers Community?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-sky-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="h-8 w-8 text-sky-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Transparency
              </h3>
              <p className="text-gray-600">
                Every work shows how it was created - AI-analyzed, human-authored, or community uploaded.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-sky-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookOpenIcon className="h-8 w-8 text-sky-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Quality Focus
              </h3>
              <p className="text-gray-600">
                AI-analyzed works have been refined through professional feedback across 7 dimensions.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-sky-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <ArrowUpTrayIcon className="h-8 w-8 text-sky-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Easy Sharing
              </h3>
              <p className="text-gray-600">
                Upload your manuscript and publish it instantly. Optional AI verification available.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
