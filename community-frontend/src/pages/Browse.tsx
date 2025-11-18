import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { worksApi } from '../api/community';
import Badge from '../components/Badge';
import type { Work, BrowseFilters } from '../types';
import { HeartIcon, EyeIcon, BookOpenIcon, MagnifyingGlassIcon, SparklesIcon } from '@heroicons/react/24/outline';

export default function Browse() {
  const [filters, setFilters] = useState<BrowseFilters>({
    sort_by: 'recent',
  });

  // Entity-based discovery state
  const [entitySearch, setEntitySearch] = useState({
    entity_name: '',
    entity_type: ''
  });
  const [isEntitySearchActive, setIsEntitySearchActive] = useState(false);

  const { data: works, isLoading } = useQuery({
    queryKey: isEntitySearchActive
      ? ['works', 'entity', entitySearch]
      : ['works', filters],
    queryFn: () => {
      if (isEntitySearchActive && entitySearch.entity_name) {
        return worksApi.browseByEntity({
          entity_name: entitySearch.entity_name,
          entity_type: entitySearch.entity_type || undefined,
          sort_by: filters.sort_by || 'created_at',
        });
      }
      return worksApi.browse(filters);
    },
  });

  const handleFilterChange = (key: keyof BrowseFilters, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const handleEntitySearch = () => {
    if (entitySearch.entity_name.trim()) {
      setIsEntitySearchActive(true);
    }
  };

  const clearEntitySearch = () => {
    setEntitySearch({ entity_name: '', entity_type: '' });
    setIsEntitySearchActive(false);
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isEntitySearchActive ? '🎯 Entity Search Results' : 'Browse Works'}
          </h1>
          <p className="text-gray-600">
            {works?.length || 0} work{works?.length !== 1 ? 's' : ''}
            {isEntitySearchActive
              ? ` featuring "${entitySearch.entity_name}"${entitySearch.entity_type ? ` (${entitySearch.entity_type})` : ''}`
              : ' available'}
          </p>
        </div>

        {/* NEW: Entity-Based Discovery */}
        <div className="bg-gradient-to-br from-purple-50 via-blue-50 to-sky-50 border-2 border-purple-200 rounded-xl p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <SparklesIcon className="h-6 w-6 text-purple-600" />
            <h2 className="text-lg font-bold text-gray-900">🎯 NEW: Entity-Based Discovery</h2>
          </div>
          <p className="text-sm text-gray-700 mb-4">
            Find stories by characters, locations, or themes! Try searching for "Mickey", "Shanghai", or "AI"
          </p>

          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-1">
              <label htmlFor="entity_name" className="block text-sm font-medium text-gray-700 mb-2">
                Entity Name
              </label>
              <input
                id="entity_name"
                type="text"
                value={entitySearch.entity_name}
                onChange={(e) => setEntitySearch({ ...entitySearch, entity_name: e.target.value })}
                placeholder="e.g., Mickey, Shanghai, AI..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleEntitySearch()}
              />
            </div>

            <div className="md:col-span-1">
              <label htmlFor="entity_type" className="block text-sm font-medium text-gray-700 mb-2">
                Entity Type (Optional)
              </label>
              <select
                id="entity_type"
                value={entitySearch.entity_type}
                onChange={(e) => setEntitySearch({ ...entitySearch, entity_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Any Type</option>
                <option value="character">Character</option>
                <option value="location">Location</option>
                <option value="theme">Theme</option>
                <option value="object">Object</option>
                <option value="organization">Organization</option>
              </select>
            </div>

            <div className="md:col-span-1 flex items-end gap-2">
              <button
                onClick={handleEntitySearch}
                disabled={!entitySearch.entity_name.trim()}
                className="flex-1 px-6 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <MagnifyingGlassIcon className="h-5 w-5" />
                Search
              </button>
              {isEntitySearchActive && (
                <button
                  onClick={clearEntitySearch}
                  className="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {isEntitySearchActive && (
            <div className="mt-4 p-3 bg-purple-100 border border-purple-300 rounded-lg">
              <p className="text-sm text-purple-900">
                <strong>Searching for:</strong> {entitySearch.entity_name}
                {entitySearch.entity_type && ` (${entitySearch.entity_type})`}
              </p>
            </div>
          )}
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
