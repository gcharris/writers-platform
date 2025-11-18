/**
 * Analytics Dashboard Component
 * Display graph statistics, central entities, and type distributions
 */

import React, { useState, useEffect } from 'react';
import { GraphStats } from '../../types/knowledge-graph';

interface AnalyticsDashboardProps {
  projectId: string;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  projectId,
}) => {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch graph stats
  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(
          `/api/knowledge-graph/projects/${projectId}/graph/stats`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch stats');
        }

        const data = await response.json();
        setStats(data);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-900 rounded-lg">
        <div className="text-white">Loading analytics...</div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-900 rounded-lg">
        <div className="text-red-400">Failed to load analytics</div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard bg-gray-900 text-white p-6 rounded-lg space-y-6">
      <h2 className="text-2xl font-bold">Knowledge Graph Analytics</h2>

      {/* Overview stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="text-3xl font-bold text-blue-400">{stats.entity_count}</div>
          <div className="text-sm text-gray-400 mt-1">Total Entities</div>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="text-3xl font-bold text-green-400">{stats.relationship_count}</div>
          <div className="text-sm text-gray-400 mt-1">Total Relationships</div>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <div className="text-3xl font-bold text-purple-400">{stats.scene_count}</div>
          <div className="text-sm text-gray-400 mt-1">Scenes Analyzed</div>
        </div>
      </div>

      {/* Extraction stats */}
      {stats.extraction_stats && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Extraction Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold">{stats.extraction_stats.total}</div>
              <div className="text-xs text-gray-400">Total Extractions</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-400">{stats.extraction_stats.successful}</div>
              <div className="text-xs text-gray-400">Successful</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">{stats.extraction_stats.failed}</div>
              <div className="text-xs text-gray-400">Failed</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{(stats.extraction_stats.success_rate * 100).toFixed(1)}%</div>
              <div className="text-xs text-gray-400">Success Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Central entities */}
      {stats.central_entities && stats.central_entities.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Most Central Entities</h3>
          <p className="text-sm text-gray-400 mb-4">
            Based on PageRank centrality - these entities have the most important connections
          </p>
          <div className="space-y-3">
            {stats.central_entities.map((item, index) => (
              <div
                key={item.entity_id}
                className="flex items-center justify-between p-3 bg-gray-700 rounded"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 flex items-center justify-center bg-blue-600 rounded-full font-bold text-sm">
                    #{index + 1}
                  </div>
                  <div>
                    <div className="font-semibold">{item.name}</div>
                    <div className="text-xs text-gray-400">Entity ID: {item.entity_id}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-blue-400">
                    {(item.centrality * 100).toFixed(2)}
                  </div>
                  <div className="text-xs text-gray-400">Centrality</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Graph density and connectivity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Graph Density</h3>
          <div className="flex items-end gap-2">
            <div className="text-4xl font-bold text-yellow-400">
              {stats.relationship_count > 0 && stats.entity_count > 0
                ? ((stats.relationship_count / (stats.entity_count * (stats.entity_count - 1))) * 100).toFixed(2)
                : '0.00'}%
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            Measure of how connected the graph is (actual edges / possible edges)
          </p>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Average Connections</h3>
          <div className="flex items-end gap-2">
            <div className="text-4xl font-bold text-teal-400">
              {stats.entity_count > 0
                ? (stats.relationship_count / stats.entity_count).toFixed(1)
                : '0.0'}
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            Average number of relationships per entity
          </p>
        </div>
      </div>

      {/* Tips for improvement */}
      {stats.entity_count < 10 && (
        <div className="bg-blue-900 bg-opacity-30 border border-blue-500 p-4 rounded-lg">
          <div className="flex items-start gap-3">
            <div className="text-blue-400 text-xl">💡</div>
            <div>
              <div className="font-semibold text-blue-300 mb-1">Tip: Build Your Knowledge Graph</div>
              <div className="text-sm text-gray-300">
                You have {stats.entity_count} entities. Extract more scenes to build a richer knowledge graph!
              </div>
            </div>
          </div>
        </div>
      )}

      {stats.extraction_stats && stats.extraction_stats.success_rate < 0.8 && stats.extraction_stats.total > 5 && (
        <div className="bg-yellow-900 bg-opacity-30 border border-yellow-500 p-4 rounded-lg">
          <div className="flex items-start gap-3">
            <div className="text-yellow-400 text-xl">⚠️</div>
            <div>
              <div className="font-semibold text-yellow-300 mb-1">Extraction Success Rate Low</div>
              <div className="text-sm text-gray-300">
                {stats.extraction_stats.failed} of {stats.extraction_stats.total} extractions failed.
                Try using the NER extractor for faster, more reliable results.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
