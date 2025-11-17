import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { worksApi } from '../api/community';
import { ArrowUpTrayIcon, DocumentTextIcon, XMarkIcon, SparklesIcon } from '@heroicons/react/24/outline';

export default function Upload() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [genre, setGenre] = useState('');
  const [description, setDescription] = useState('');
  const [claimHumanAuthored, setClaimHumanAuthored] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile) throw new Error('No file selected');
      return worksApi.upload(selectedFile, {
        title,
        description,
        genre,
        claim_human_authored: claimHumanAuthored,
      });
    },
    onSuccess: (work) => {
      navigate(`/works/${work.id}`);
    },
  });

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
      setSelectedFile(files[0]);
      if (!title) {
        setTitle(files[0].name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
      if (!title) {
        setTitle(files[0].name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    await uploadMutation.mutateAsync();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Share Your Work</h1>
          <p className="text-gray-600 mt-1">
            Upload your manuscript to Writers Community
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          {/* File drop zone */}
          {!selectedFile ? (
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragging
                  ? 'border-sky-500 bg-sky-50'
                  : 'border-gray-300 hover:border-sky-300'
              }`}
              onDragEnter={handleDragEnter}
              onDragOver={(e) => e.preventDefault()}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <ArrowUpTrayIcon className="h-16 w-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Drop your file here
              </h3>
              <p className="text-gray-500 mb-4">or</p>
              <label className="inline-flex items-center px-6 py-3 bg-sky-600 text-white font-medium rounded-lg cursor-pointer hover:bg-sky-700 transition-colors">
                Browse Files
                <input
                  type="file"
                  className="hidden"
                  accept=".docx,.pdf,.txt"
                  onChange={handleFileSelect}
                />
              </label>
              <p className="text-sm text-gray-500 mt-4">
                Supports DOCX, PDF, and TXT (max 10MB)
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Selected file */}
              <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <DocumentTextIcon className="h-10 w-10 text-sky-600" />
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              {/* Metadata */}
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  id="title"
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="Enter work title"
                />
              </div>

              <div>
                <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-2">
                  Genre
                </label>
                <select
                  id="genre"
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                >
                  <option value="">Select a genre</option>
                  <option value="Science Fiction">Science Fiction</option>
                  <option value="Fantasy">Fantasy</option>
                  <option value="Mystery">Mystery</option>
                  <option value="Romance">Romance</option>
                  <option value="Thriller">Thriller</option>
                  <option value="Literary Fiction">Literary Fiction</option>
                  <option value="Horror">Horror</option>
                  <option value="Historical">Historical</option>
                </select>
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="Brief description of your work"
                />
              </div>

              {/* Human authorship claim */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    id="humanAuthored"
                    checked={claimHumanAuthored}
                    onChange={(e) => setClaimHumanAuthored(e.target.checked)}
                    className="mt-1 h-4 w-4 text-sky-600 focus:ring-sky-500 border-gray-300 rounded"
                  />
                  <div className="flex-1">
                    <label htmlFor="humanAuthored" className="block font-medium text-gray-900 cursor-pointer">
                      This work was written entirely by me, without AI assistance
                    </label>
                    <p className="text-sm text-gray-600 mt-1">
                      If checked, our AI detection system will verify your claim and award a "Human-Authored" badge if verified.
                    </p>
                  </div>
                </div>
              </div>

              {/* Upload progress */}
              {uploadMutation.isPending && (
                <div>
                  <div className="text-sm text-gray-600 mb-2">
                    <span>Uploading, parsing, and analyzing...</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-sky-600 h-2 rounded-full animate-pulse" style={{ width: '100%' }} />
                  </div>
                </div>
              )}

              {/* Error */}
              {uploadMutation.isError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  Upload failed. Please try again.
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => navigate('/browse')}
                  className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadMutation.isPending}
                  className="flex-1 px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadMutation.isPending ? 'Publishing...' : 'Publish to Community'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Info section */}
        <div className="mt-8 bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <SparklesIcon className="h-8 w-8 text-purple-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Want professional AI feedback first?</h3>
              <p className="text-gray-700 text-sm mb-3">
                Get detailed analysis from 5 AI models before publishing. Improve your work with professional feedback across 7 dimensions.
              </p>
              <a
                href="https://writersfactory.app"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
              >
                Try Writers Factory →
              </a>
            </div>
          </div>
        </div>

        {/* What happens next */}
        <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">What happens after upload?</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-sky-600 font-bold">1.</span>
              <span>Your file will be parsed and formatted for reading</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-sky-600 font-bold">2.</span>
              <span>If you claimed human authorship, our AI will verify your work</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-sky-600 font-bold">3.</span>
              <span>Appropriate badges will be assigned based on analysis results</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-sky-600 font-bold">4.</span>
              <span>Your work will appear in the community browse page</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
