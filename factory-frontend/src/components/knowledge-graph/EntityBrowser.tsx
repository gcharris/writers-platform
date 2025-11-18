/**
 * Entity Browser Component
 * Browse, search, and filter entities in the knowledge graph
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Entity, EntityType } from '../../types/knowledge-graph';
import { debounce } from '../../utils/debounce';

interface EntityBrowserProps {
  projectId: string;
  onEntitySelect: (entity: Entity) => void;
  selectedEntityId?: string;
}

const ENTITY_TYPE_LABELS: Record<EntityType, string> = {
  character: 'Character',
  location: 'Location',
  object: 'Object',
  concept: 'Concept',
  event: 'Event',
  organization: 'Organization',
  theme: 'Theme',
};

const ENTITY_TYPE_COLORS: Record<EntityType, string> = {
  character: 'bg-red-500',
  location: 'bg-teal-500',
  object: 'bg-green-400',
  concept: 'bg-yellow-400',
  event: 'bg-pink-400',
  organization: 'bg-purple-400',
  theme: 'bg-orange-300',
};

export const EntityBrowser: React.FC<EntityBrowserProps> = ({
  projectId,
  onEntitySelect,
  selectedEntityId,
}) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [filteredEntities, setFilteredEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<Set<EntityType>>(new Set());
  const [sortBy, setSortBy] = useState<'name' | 'mentions'>('name');

  // Fetch entities
  useEffect(() => {
    const fetchEntities = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(
          `/api/knowledge-graph/projects/${projectId}/entities`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch entities');
        }

        const data = await response.json();
        setEntities(data);
        setFilteredEntities(data);
      } catch (err) {
        console.error('Error fetching entities:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEntities();
  }, [projectId]);

  // Filter and sort entities
  useEffect(() => {
    let filtered = entities;

    // Filter by type
    if (selectedTypes.size > 0) {
      filtered = filtered.filter(e => selectedTypes.has(e.type));
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(e =>
        e.name.toLowerCase().includes(query) ||
        e.description.toLowerCase().includes(query) ||
        (e.aliases && e.aliases.some(alias =>
          alias.toLowerCase().includes(query)
        ))
      );
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'mentions':
          return (b.mentions || 0) - (a.mentions || 0);
        default:
          return 0;
      }
    });

    setFilteredEntities(filtered);
  }, [entities, selectedTypes, searchQuery, sortBy]);

  // Debounced search
  const debouncedSetSearchQuery = useCallback(
    debounce((value: string) => setSearchQuery(value), 300),
    []
  );

  // Toggle entity type filter
  const toggleTypeFilter = (type: EntityType) => {
    const newSelectedTypes = new Set(selectedTypes);
    if (newSelectedTypes.has(type)) {
      newSelectedTypes.delete(type);
    } else {
      newSelectedTypes.add(type);
    }
    setSelectedTypes(newSelectedTypes);
  };

  // Handle entity click
  const handleEntityClick = async (entity: Entity) => {
    onEntitySelect(entity);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-400">Loading entities...</div>
      </div>
    );
  }

  return (
    <div className="entity-browser flex flex-col h-full bg-gray-900 text-white">
      {/* Search bar */}
      <div className="p-4 border-b border-gray-700">
        <input
          type="text"
          placeholder="Search entities..."
          onChange={(e) => debouncedSetSearchQuery(e.target.value)}
          className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Type filters */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex flex-wrap gap-2">
          {Object.entries(ENTITY_TYPE_LABELS).map(([type, label]) => (
            <button
              key={type}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                selectedTypes.has(type as EntityType)
                  ? `${ENTITY_TYPE_COLORS[type as EntityType]} text-white`
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              onClick={() => toggleTypeFilter(type as EntityType)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Sort controls */}
      <div className="px-4 py-2 border-b border-gray-700 flex items-center gap-2 text-sm">
        <label className="text-gray-400">Sort by:</label>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="name">Name</option>
          <option value="mentions">Mentions</option>
        </select>
      </div>

      {/* Entity list */}
      <div className="flex-1 overflow-y-auto">
        {filteredEntities.length === 0 ? (
          <div className="p-8 text-center text-gray-400">No entities found</div>
        ) : (
          <div className="divide-y divide-gray-700">
            {filteredEntities.map(entity => (
              <div
                key={entity.id}
                className={`p-4 cursor-pointer transition-colors hover:bg-gray-800 ${
                  selectedEntityId === entity.id ? 'bg-gray-800 border-l-4 border-blue-500' : ''
                }`}
                onClick={() => handleEntityClick(entity)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${ENTITY_TYPE_COLORS[entity.type]} text-white`}>
                    {ENTITY_TYPE_LABELS[entity.type]}
                  </span>
                  <span className="font-semibold">{entity.name}</span>
                </div>

                {entity.description && (
                  <div className="text-sm text-gray-400 mb-2 line-clamp-2">
                    {entity.description}
                  </div>
                )}

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {entity.mentions > 0 && (
                    <span>
                      {entity.mentions} mention{entity.mentions !== 1 ? 's' : ''}
                    </span>
                  )}
                  {entity.verified && (
                    <span className="text-green-400">✓ Verified</span>
                  )}
                </div>

                {entity.aliases && entity.aliases.length > 0 && (
                  <div className="mt-2 text-xs text-gray-500">
                    Aliases: {entity.aliases.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="px-4 py-2 border-t border-gray-700 text-xs text-gray-400">
        Showing {filteredEntities.length} of {entities.length} entities
      </div>
    </div>
  );
};

export default EntityBrowser;
