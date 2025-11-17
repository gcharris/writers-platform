import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpTrayIcon, PencilSquareIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      navigate('/upload', { state: { file: files[0] } });
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      navigate('/upload', { state: { file: files[0] } });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Writers Factory
          </h1>
          <p className="text-xl text-gray-600">
            AI-powered analysis and refinement for your writing
          </p>
        </div>

        {/* Two-column layout */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {/* Left: Upload existing draft */}
          <div
            className={`bg-white rounded-2xl shadow-lg p-8 border-2 transition-all ${
              isDragging
                ? 'border-indigo-500 bg-indigo-50'
                : 'border-gray-200 hover:border-indigo-300'
            }`}
            onDragEnter={handleDragEnter}
            onDragOver={(e) => e.preventDefault()}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="text-center">
              <ArrowUpTrayIcon className="h-16 w-16 mx-auto text-indigo-600 mb-4" />
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                I Have a Draft
              </h2>
              <p className="text-gray-600 mb-6">
                Upload your manuscript for AI analysis
              </p>

              {/* Upload button */}
              <label className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg cursor-pointer hover:bg-indigo-700 transition-colors">
                <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
                Upload File
                <input
                  type="file"
                  className="hidden"
                  accept=".docx,.pdf,.txt"
                  onChange={handleFileSelect}
                />
              </label>

              {/* Supported formats */}
              <p className="text-sm text-gray-500 mt-4">
                Supports DOCX, PDF, and TXT files
              </p>

              {/* Drag and drop hint */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-500">
                  Or drag and drop your file here
                </p>
              </div>
            </div>
          </div>

          {/* Right: Start new project */}
          <div className="bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-200 hover:border-purple-300 transition-all">
            <div className="text-center">
              <PencilSquareIcon className="h-16 w-16 mx-auto text-purple-600 mb-4" />
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                I'm Just Starting
              </h2>
              <p className="text-gray-600 mb-6">
                Create a new project from scratch
              </p>

              {/* Create button */}
              <button
                onClick={() => navigate('/dashboard?new=true')}
                className="inline-flex items-center px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
              >
                <PencilSquareIcon className="h-5 w-5 mr-2" />
                Start New Project
              </button>

              {/* Features list */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <ul className="text-sm text-gray-600 space-y-2 text-left">
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Rich text editor with auto-save</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>Scene-by-scene organization</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-600 mr-2">•</span>
                    <span>AI analysis and feedback</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="text-center">
          <p className="text-gray-600 mb-2">
            Looking for published works?
          </p>
          <a
            href="https://writerscommunity.app"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
            target="_blank"
            rel="noopener noreferrer"
          >
            Browse Writers Community →
          </a>
        </div>
      </div>
    </div>
  );
}
