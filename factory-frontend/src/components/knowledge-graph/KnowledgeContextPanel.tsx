/**
 * Knowledge Context Panel
 * Display relevant knowledge graph context for current writing task
 */

import React, { useState, useEffect } from 'react';
import { Entity, Relationship, EntityType } from '../../types/knowledge-graph';

interface KnowledgeContextPanelProps {
  projectId: string;
  sceneId?: string;
  contextQueries?: string[];  // User-defined context questions
}

interface ContextResult {
  query: string;
  entities: Entity[];
  relationships: Relationship[];
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

export const KnowledgeContextPanel: React.FC<KnowledgeContextPanelProps> = ({
  projectId,
  sceneId,
  contextQueries = [],
}) => {
  const [contextResults, setContextResults] = useState<ContextResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [customQuery, setCustomQuery] = useState('');

  // Fetch context
  useEffect(() => {
    if (contextQueries.length === 0) return;

    const fetchContext = async () => {
      setLoading(true);
      try {
        const results: ContextResult[] = [];

        for (const query of contextQueries) {
          const token = localStorage.getItem('auth_token');

          // Query entities
          const entityResponse = await fetch(
            `/api/knowledge-graph/projects/${projectId}/entities?search=${encodeURIComponent(query)}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );

          if (entityResponse.ok) {
            const entityData = await entityResponse.json();

            results.push({
              query,
              entities: entityData,
              relationships: [],
            });
          }
        }

        setContextResults(results);
      } catch (err) {
        console.error('Error fetching context:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchContext();
  }, [projectId, contextQueries]);

  // Add custom query
  const handleAddQuery = async () => {
    if (!customQuery.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('auth_token');

      // Query entities
      const entityResponse = await fetch(
        `/api/knowledge-graph/projects/${projectId}/entities?search=${encodeURIComponent(customQuery)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (entityResponse.ok) {
        const entityData = await entityResponse.json();

        setContextResults(prev => [
          ...prev,
          { query: customQuery, entities: entityData, relationships: [] },
        ]);
      }

      setCustomQuery('');
    } catch (err) {
      console.error('Error fetching custom context:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="knowledge-context-panel bg-gray-900 text-white p-6 rounded-lg">
      <h3 className="text-2xl font-bold mb-6">Knowledge Context</h3>

      {/* Add custom query */}
      <div className="add-query mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={customQuery}
            onChange={(e) => setCustomQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddQuery()}
            placeholder="Ask about characters, locations, events..."
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleAddQuery}
            disabled={loading || !customQuery.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
          >
            Add Context
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Ask questions like "Who are the main characters?" or "What locations are mentioned?"
        </p>
      </div>

      {/* Context results */}
      {loading && contextResults.length === 0 ? (
        <div className="text-center py-8 text-gray-400">Loading context...</div>
      ) : contextResults.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">💡</div>
          <p className="font-semibold mb-1">No context queries yet</p>
          <p className="text-sm">Add one above to get started</p>
        </div>
      ) : (
        <div className="context-results space-y-6">
          {contextResults.map((result, index) => (
            <div key={index} className="context-result bg-gray-800 p-4 rounded-lg">
              <h4 className="context-query text-lg font-semibold mb-4 text-blue-300">
                {result.query}
              </h4>

              {result.entities.length > 0 ? (
                <div className="context-entities space-y-3">
                  {result.entities.map(entity => (
                    <div key={entity.id} className="context-entity bg-gray-700 p-3 rounded-lg">
                      <div className="entity-header flex items-center gap-3 mb-2">
                        <span className={`${ENTITY_TYPE_COLORS[entity.type]} w-2 h-2 rounded-full flex-shrink-0`}></span>
                        <span className="font-semibold flex-1">{entity.name}</span>
                        <span className="text-xs text-gray-400 capitalize">{entity.type}</span>
                      </div>

                      {entity.description && (
                        <div className="entity-description text-sm text-gray-300 mb-2">
                          {entity.description}
                        </div>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        {entity.mentions > 0 && (
                          <span>{entity.mentions} mentions</span>
                        )}
                        {entity.verified && (
                          <span className="text-green-400">✓ Verified</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-results text-center py-4 text-gray-400">
                  No entities found for this query
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default KnowledgeContextPanel;
