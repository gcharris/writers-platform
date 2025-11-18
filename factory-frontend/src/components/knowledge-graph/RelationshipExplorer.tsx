/**
 * Relationship Explorer Component
 * Explore relationships between entities and find paths
 */

import React, { useState, useEffect } from 'react';
import { Relationship, Entity, PathQueryResult } from '../../types/knowledge-graph';

interface RelationshipExplorerProps {
  projectId: string;
  sourceEntityId?: string;
  targetEntityId?: string;
}

export const RelationshipExplorer: React.FC<RelationshipExplorerProps> = ({
  projectId,
  sourceEntityId,
  targetEntityId,
}) => {
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<string>('all');
  const [pathFinding, setPathFinding] = useState(false);
  const [pathResult, setPathResult] = useState<PathQueryResult | null>(null);
  const [sourceEntity, setSourceEntity] = useState<Entity | null>(null);
  const [targetEntity, setTargetEntity] = useState<Entity | null>(null);

  // Fetch source and target entities
  useEffect(() => {
    const fetchEntities = async () => {
      const token = localStorage.getItem('auth_token');

      if (sourceEntityId) {
        try {
          const response = await fetch(
            `/api/knowledge-graph/projects/${projectId}/entities/${sourceEntityId}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          if (response.ok) {
            const data = await response.json();
            setSourceEntity(data.entity || data);
          }
        } catch (err) {
          console.error('Error fetching source entity:', err);
        }
      }

      if (targetEntityId) {
        try {
          const response = await fetch(
            `/api/knowledge-graph/projects/${projectId}/entities/${targetEntityId}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          if (response.ok) {
            const data = await response.json();
            setTargetEntity(data.entity || data);
          }
        } catch (err) {
          console.error('Error fetching target entity:', err);
        }
      }
    };

    fetchEntities();
  }, [projectId, sourceEntityId, targetEntityId]);

  // Fetch relationships
  useEffect(() => {
    const fetchRelationships = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('auth_token');
        let url = `/api/knowledge-graph/projects/${projectId}/relationships`;
        const params = new URLSearchParams();

        if (sourceEntityId) params.append('source_id', sourceEntityId);
        if (targetEntityId) params.append('target_id', targetEntityId);
        if (filterType !== 'all') params.append('relation_type', filterType);

        if (params.toString()) {
          url += `?${params.toString()}`;
        }

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch relationships');
        }

        const data = await response.json();
        setRelationships(data);
      } catch (err) {
        console.error('Error fetching relationships:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRelationships();
  }, [projectId, sourceEntityId, targetEntityId, filterType]);

  // Find path between entities
  const findPath = async () => {
    if (!sourceEntityId || !targetEntityId) return;

    setPathFinding(true);
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/path`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            source_id: sourceEntityId,
            target_id: targetEntityId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to find path');
      }

      const data = await response.json();
      setPathResult(data);
    } catch (err) {
      console.error('Error finding path:', err);
      setPathResult({ found: false, message: 'Error finding path' });
    } finally {
      setPathFinding(false);
    }
  };

  return (
    <div className="relationship-explorer bg-gray-900 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold mb-6">Relationship Explorer</h2>

      {/* Filter controls */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-400 mb-2">Filter by type:</label>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">All Types</option>
          <option value="knows">Knows</option>
          <option value="conflicts_with">Conflicts With</option>
          <option value="located_in">Located In</option>
          <option value="owns">Owns</option>
          <option value="member_of">Member Of</option>
          <option value="related_to">Related To</option>
          <option value="loves">Loves</option>
          <option value="fears">Fears</option>
        </select>
      </div>

      {/* Path finding */}
      {sourceEntity && targetEntity && (
        <div className="mb-6 p-4 bg-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm">
              <span className="text-gray-400">From: </span>
              <span className="text-white font-semibold">{sourceEntity.name}</span>
              <span className="text-gray-400 mx-2">→</span>
              <span className="text-gray-400">To: </span>
              <span className="text-white font-semibold">{targetEntity.name}</span>
            </div>
            <button
              onClick={findPath}
              disabled={pathFinding}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
            >
              {pathFinding ? 'Finding path...' : 'Find Path'}
            </button>
          </div>

          {pathResult && pathResult.found && pathResult.entities && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">
                Path Found ({pathResult.length} steps):
              </h3>
              <div className="flex flex-wrap items-center gap-2">
                {pathResult.entities.map((entity, index) => (
                  <React.Fragment key={entity.id}>
                    <span className="px-3 py-1 bg-gray-700 rounded text-sm">
                      {entity.name}
                    </span>
                    {index < pathResult.entities!.length - 1 && (
                      <span className="text-gray-400">→</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          )}

          {pathResult && !pathResult.found && (
            <div className="mt-4 text-red-400 text-sm">
              {pathResult.message || 'No path found between entities'}
            </div>
          )}
        </div>
      )}

      {/* Relationship list */}
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Relationships {relationships.length > 0 && `(${relationships.length})`}
        </h3>

        {loading ? (
          <div className="text-center py-8 text-gray-400">Loading relationships...</div>
        ) : relationships.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No relationships found</div>
        ) : (
          <div className="space-y-3">
            {relationships.map((relationship, index) => (
              <div
                key={`${relationship.source}-${relationship.target}-${index}`}
                className="p-4 bg-gray-800 rounded-lg hover:bg-gray-750 transition-colors"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="px-2 py-1 bg-blue-600 rounded text-xs font-medium">
                    {relationship.relation.replace(/_/g, ' ')}
                  </span>
                  <span className="text-sm text-gray-400">
                    {relationship.source} → {relationship.target}
                  </span>
                </div>

                {relationship.description && (
                  <p className="text-sm text-gray-300 mb-2">{relationship.description}</p>
                )}

                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {relationship.strength !== undefined && (
                    <span>Strength: {(relationship.strength * 100).toFixed(0)}%</span>
                  )}
                  {relationship.scenes && relationship.scenes.length > 0 && (
                    <span>{relationship.scenes.length} scene(s)</span>
                  )}
                  {relationship.valence !== undefined && (
                    <span className={relationship.valence > 0 ? 'text-green-400' : relationship.valence < 0 ? 'text-red-400' : ''}>
                      Valence: {relationship.valence > 0 ? '+' : ''}{relationship.valence.toFixed(2)}
                    </span>
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

export default RelationshipExplorer;
