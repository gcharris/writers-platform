import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { worksApi } from '../api/community';
import Badge from '../components/Badge';
import type { Work, BrowseFilters } from '../types';
import { HeartIcon, EyeIcon, BookOpenIcon } from '@heroicons/react/24/outline';

export default function Browse() {
  const [filters, setFilters] = useState<BrowseFilters>({
    sort_by: 'recent',
  });

  const { data: works, isLoading } = useQuery({
    queryKey: ['works', filters],
    queryFn: () => worksApi.browse(filters),
  });

  const handleFilterChange = (key: keyof BrowseFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}k`;
    }
    return num.toString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading works...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Browse Works</h1>
          <p className="text-gray-600">
            {works?.length || 0} work{works?.length !== 1 ? 's' : ''} available
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid md:grid-cols-4 gap-4">
            {/* Search */}
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                id="search"
                type="text"
                value={filters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                placeholder="Title or description..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>

            {/* Genre */}
            <div>
              <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-2">
                Genre
              </label>
              <select
                id="genre"
                value={filters.genre || ''}
                onChange={(e) => handleFilterChange('genre', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">All Genres</option>
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

            {/* Badge Filter */}
            <div>
              <label htmlFor="badge" className="block text-sm font-medium text-gray-700 mb-2">
                Badge Type
              </label>
              <select
                id="badge"
                value={filters.badge_type || ''}
                onChange={(e) => handleFilterChange('badge_type', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">All Badges</option>
                <option value="ai_analyzed">AI-Analyzed</option>
                <option value="human_verified">Human-Verified</option>
                <option value="human_self">Human-Self</option>
                <option value="community_upload">Community Upload</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label htmlFor="sort" className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                id="sort"
                value={filters.sort_by || 'recent'}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="recent">Most Recent</option>
                <option value="popular">Most Popular</option>
                <option value="liked">Most Liked</option>
              </select>
            </div>
          </div>
        </div>

        {/* Works Grid */}
        {works && works.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {works.map((work: Work) => (
              <Link
                key={work.id}
                to={`/works/${work.id}`}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                {/* Badges */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {work.badges.map((badge) => (
                    <Badge key={badge.id} badge={badge} size="sm" />
                  ))}
                </div>

                {/* Title & Author */}
                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {work.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  by {work.author.username}
                </p>

                {/* Genre */}
                {work.genre && (
                  <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded mb-3">
                    {work.genre}
                  </span>
                )}

                {/* Description */}
                {work.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                    {work.description}
                  </p>
                )}

                {/* Stats */}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <BookOpenIcon className="h-4 w-4" />
                    <span>{formatNumber(work.word_count)} words</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <EyeIcon className="h-4 w-4" />
                    <span>{formatNumber(work.view_count)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <HeartIcon className="h-4 w-4" />
                    <span>{formatNumber(work.like_count)}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <BookOpenIcon className="h-16 w-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No works found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your filters or check back later</p>
            <Link
              to="/upload"
              className="inline-block px-6 py-3 bg-sky-600 text-white font-medium rounded-lg hover:bg-sky-700 transition-colors"
            >
              Be the first to share
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
