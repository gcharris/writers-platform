/**
 * Graph-Powered Search Component
 * Semantic search using knowledge graph structure
 */

import React, { useState } from 'react';
import { Entity, EntityType } from '../../types/knowledge-graph';

interface GraphPoweredSearchProps {
  projectId: string;
  onResultSelect: (entity: Entity) => void;
}

interface SearchResult {
  entity: Entity;
  relevance: number;
  path?: Entity[];  // Path from query to result
  context: string;
}

const ENTITY_TYPE_COLORS: Record<EntityType, string> = {
  character: 'bg-red-500',
  location: 'bg-teal-500',
  object: 'bg-green-400',
  concept: 'bg-yellow-400',
  event: 'bg-pink-400',
  organization: 'bg-purple-400',
  theme: 'bg-orange-300',
};

export const GraphPoweredSearch: React.FC<GraphPoweredSearchProps> = ({
  projectId,
  onResultSelect,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchType, setSearchType] = useState<'direct' | 'semantic' | 'path'>('semantic');

  // Perform search
  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearching(true);
    try {
      const token = localStorage.getItem('auth_token');

      // For now, use the entities endpoint with search parameter
      // In production, this would call a dedicated graph search endpoint
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/entities?search=${encodeURIComponent(query)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();

      // Transform entity data to search results
      const searchResults: SearchResult[] = data.map((entity: Entity) => {
        // Calculate relevance based on name match
        const nameLower = entity.name.toLowerCase();
        const queryLower = query.toLowerCase();
        const relevance = nameLower === queryLower ? 1.0
          : nameLower.includes(queryLower) ? 0.8
          : entity.description?.toLowerCase().includes(queryLower) ? 0.6
          : 0.4;

        return {
          entity,
          relevance,
          context: entity.description || `${entity.type} from your story`,
        };
      });

      // Sort by relevance
      searchResults.sort((a, b) => b.relevance - a.relevance);

      setResults(searchResults);
    } catch (err) {
      console.error('Search error:', err);
      alert('Search failed');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="graph-powered-search bg-gray-900 text-white p-6 rounded-lg">
      {/* Search bar */}
      <div className="search-bar mb-6">
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search knowledge graph..."
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <select
            value={searchType}
            onChange={(e) => setSearchType(e.target.value as any)}
            className="px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="direct">Direct Match</option>
            <option value="semantic">Semantic Search</option>
            <option value="path">Path Finding</option>
          </select>

          <button
            onClick={handleSearch}
            disabled={searching || !query.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="text-xs text-gray-400">
          {searchType === 'direct' && 'Find exact name matches'}
          {searchType === 'semantic' && 'Find related entities using AI understanding'}
          {searchType === 'path' && 'Find connections between entities'}
        </div>
      </div>

      {/* Search results */}
      <div className="search-results">
        {searching ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🔍</div>
            <p>Searching knowledge graph...</p>
          </div>
        ) : results.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-2">🔎</div>
            <p>{query ? 'No results found' : 'Enter a search query'}</p>
            {query && (
              <p className="text-sm mt-2">Try different keywords or search type</p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-sm text-gray-400 mb-4">
              Found {results.length} result{results.length !== 1 ? 's' : ''}
            </div>
            {results.map((result, index) => (
              <div
                key={`${result.entity.id}-${index}`}
                className="search-result-item bg-gray-800 p-4 rounded-lg hover:bg-gray-750 transition-colors cursor-pointer"
                onClick={() => onResultSelect(result.entity)}
              >
                <div className="result-header flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3 flex-1">
                    <span className={`${ENTITY_TYPE_COLORS[result.entity.type]} w-2 h-2 rounded-full flex-shrink-0`}></span>
                    <span className="font-semibold text-lg">{result.entity.name}</span>
                    <span className="text-xs text-gray-400 capitalize">{result.entity.type}</span>
                  </div>
                  <span className="relevance-score px-2 py-1 bg-blue-900 bg-opacity-50 text-blue-300 rounded text-xs font-medium">
                    {Math.round(result.relevance * 100)}% match
                  </span>
                </div>

                {result.context && (
                  <div className="result-context text-sm text-gray-300 mb-2">
                    {result.context}
                  </div>
                )}

                {result.path && result.path.length > 0 && (
                  <div className="result-path text-xs text-gray-400">
                    <span className="font-semibold">Path:</span>{' '}
                    {result.path.map(e => e.name).join(' → ')}
                  </div>
                )}

                <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                  {result.entity.mentions > 0 && (
                    <span>{result.entity.mentions} mentions</span>
                  )}
                  {result.entity.verified && (
                    <span className="text-green-400">✓ Verified</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphPoweredSearch;
