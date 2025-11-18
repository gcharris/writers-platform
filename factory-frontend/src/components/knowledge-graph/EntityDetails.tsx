/**
 * Entity Details Component
 * Display detailed information about a selected entity
 * Shows properties, relationships, and connected entities
 */

import React, { useState, useEffect } from 'react';
import { Entity } from '../../types/knowledge-graph';

interface EntityDetailsProps {
  projectId: string;
  entityId: string;
  onClose: () => void;
  onNavigateToEntity?: (entityId: string) => void;
}

const ENTITY_TYPE_COLORS: Record<string, string> = {
  character: 'bg-red-500',
  location: 'bg-teal-500',
  object: 'bg-green-400',
  concept: 'bg-yellow-400',
  event: 'bg-pink-400',
  organization: 'bg-purple-400',
  theme: 'bg-orange-300',
};

export const EntityDetails: React.FC<EntityDetailsProps> = ({
  projectId,
  entityId,
  onClose,
  onNavigateToEntity,
}) => {
  const [entity, setEntity] = useState<Entity | null>(null);
  const [connectedEntities, setConnectedEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  // Fetch entity details
  useEffect(() => {
    const fetchEntityDetails = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('auth_token');

        // Fetch entity with stats
        const response = await fetch(
          `/api/knowledge-graph/projects/${projectId}/entities/${entityId}?include_stats=true`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch entity details');
        }

        const data = await response.json();
        setEntity(data.entity);
        setStats(data);

        // Fetch connected entities
        const connectionsResponse = await fetch(
          `/api/knowledge-graph/projects/${projectId}/entities/${entityId}/connections?max_depth=1`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (connectionsResponse.ok) {
          const connections = await connectionsResponse.json();
          setConnectedEntities(connections);
        }
      } catch (err) {
        console.error('Error fetching entity details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEntityDetails();
  }, [projectId, entityId]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-900 p-8 rounded-lg">
          <div className="text-white">Loading entity details...</div>
        </div>
      </div>
    );
  }

  if (!entity) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-900 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-white">{entity.name}</h2>
            <span className={`px-2 py-1 rounded text-xs font-medium ${ENTITY_TYPE_COLORS[entity.type]} text-white`}>
              {entity.type}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Description */}
          {entity.description && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Description</h3>
              <p className="text-white">{entity.description}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-1">Mentions</h3>
              <p className="text-white text-lg">{entity.mentions}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-1">Confidence</h3>
              <p className="text-white text-lg">{(entity.confidence * 100).toFixed(0)}%</p>
            </div>
            {entity.verified && (
              <div>
                <h3 className="text-sm font-semibold text-gray-400 mb-1">Status</h3>
                <p className="text-green-400">✓ Verified</p>
              </div>
            )}
          </div>

          {/* Aliases */}
          {entity.aliases && entity.aliases.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Aliases</h3>
              <div className="flex flex-wrap gap-2">
                {entity.aliases.map((alias, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-800 rounded text-sm text-gray-300">
                    {alias}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Attributes */}
          {entity.attributes && Object.keys(entity.attributes).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Attributes</h3>
              <div className="space-y-2">
                {Object.entries(entity.attributes).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-2 border-b border-gray-800">
                    <span className="text-gray-400">{key}</span>
                    <span className="text-white">
                      {Array.isArray(value) ? value.join(', ') : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 📚 Research Citations (NotebookLM Sources) */}
          {entity.properties?.notebooklm_sources && entity.properties.notebooklm_sources.length > 0 && (
            <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 border border-blue-700 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-sm font-semibold text-blue-300">
                  📚 Research Citations
                </h3>
                <span className="text-xs text-gray-400">from NotebookLM</span>
              </div>
              <p className="text-xs text-gray-400 mb-3">
                This entity was grounded in research from the following sources:
              </p>
              <div className="space-y-2">
                {entity.properties.notebooklm_sources.slice(0, 5).map((source: any, index: number) => (
                  <div key={index} className="bg-gray-800/50 rounded p-3 border border-gray-700">
                    <div className="flex items-start gap-2">
                      <span className="text-blue-400 text-xs font-mono mt-0.5">[{index + 1}]</span>
                      <div className="flex-1">
                        {source.url ? (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-300 text-sm font-medium underline break-all"
                          >
                            {source.title || source.url}
                          </a>
                        ) : (
                          <p className="text-gray-300 text-sm font-medium">
                            {source.title || 'Untitled Source'}
                          </p>
                        )}
                        {source.snippet && (
                          <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                            {source.snippet}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {entity.properties.notebooklm_sources.length > 5 && (
                  <p className="text-xs text-gray-400 italic">
                    +{entity.properties.notebooklm_sources.length - 5} more sources
                  </p>
                )}
              </div>
              {entity.properties?.notebooklm_notebook_id && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <p className="text-xs text-gray-500">
                    Extracted from NotebookLM notebook: {entity.properties.notebooklm_notebook_id}
                  </p>
                </div>
              )}
              {entity.properties?.enriched_from_notebooklm && (
                <div className="mt-2 text-xs text-green-400 flex items-center gap-1">
                  ✓ <span>Enriched with research data</span>
                </div>
              )}
            </div>
          )}

          {/* Appearances */}
          {entity.appearances && entity.appearances.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">
                Appearances ({entity.appearances.length} scenes)
              </h3>
              {entity.first_appearance && (
                <p className="text-sm text-gray-400">First appeared in: Scene {entity.first_appearance}</p>
              )}
            </div>
          )}

          {/* Connection Stats */}
          {stats && stats.connections && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Connection Statistics</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-800 p-3 rounded">
                  <div className="text-gray-400 text-xs">Incoming</div>
                  <div className="text-white text-xl">{stats.connections.incoming}</div>
                </div>
                <div className="bg-gray-800 p-3 rounded">
                  <div className="text-gray-400 text-xs">Outgoing</div>
                  <div className="text-white text-xl">{stats.connections.outgoing}</div>
                </div>
                <div className="bg-gray-800 p-3 rounded">
                  <div className="text-gray-400 text-xs">Total</div>
                  <div className="text-white text-xl">{stats.connections.total}</div>
                </div>
              </div>
            </div>
          )}

          {/* Connected Entities */}
          {connectedEntities && connectedEntities.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">
                Connected Entities ({connectedEntities.length})
              </h3>
              <div className="space-y-2">
                {connectedEntities.slice(0, 10).map((connectedEntity) => (
                  <div
                    key={connectedEntity.id}
                    className="flex items-center justify-between p-3 bg-gray-800 rounded cursor-pointer hover:bg-gray-700 transition-colors"
                    onClick={() => onNavigateToEntity && onNavigateToEntity(connectedEntity.id)}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs ${ENTITY_TYPE_COLORS[connectedEntity.type]} text-white`}>
                        {connectedEntity.type}
                      </span>
                      <span className="text-white">{connectedEntity.name}</span>
                    </div>
                    <span className="text-gray-400">→</span>
                  </div>
                ))}
                {connectedEntities.length > 10 && (
                  <p className="text-sm text-gray-400">
                    +{connectedEntities.length - 10} more entities
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-6 border-t border-gray-700 flex gap-3">
          <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors">
            Edit Entity
          </button>
          <button className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors">
            Export
          </button>
          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors">
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default EntityDetails;
