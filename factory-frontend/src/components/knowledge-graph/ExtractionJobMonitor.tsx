/**
 * Extraction Job Monitor Component
 * Monitor and display status of background extraction jobs
 */

import React, { useState, useEffect } from 'react';

interface ExtractionJob {
  id: string;
  project_id: string;
  scene_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  extractor_type: 'llm' | 'ner';
  model_name?: string;
  progress: number;
  entities_found: number;
  relationships_found: number;
  cost: number;
  error?: string;
  created_at: string;
  completed_at?: string;
}

interface ExtractionJobMonitorProps {
  projectId: string;
}

export const ExtractionJobMonitor: React.FC<ExtractionJobMonitorProps> = ({
  projectId,
}) => {
  const [jobs, setJobs] = useState<ExtractionJob[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch jobs
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(
          `/api/knowledge-graph/projects/${projectId}/extract/jobs`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch jobs');
        }

        const data = await response.json();
        setJobs(data.jobs || data);
      } catch (err) {
        console.error('Error fetching jobs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();

    // Poll for updates every 3 seconds
    const interval = setInterval(fetchJobs, 3000);

    return () => clearInterval(interval);
  }, [projectId]);

  // Cancel job
  const cancelJob = async (jobId: string) => {
    try {
      const token = localStorage.getItem('auth_token');
      await fetch(
        `/api/knowledge-graph/projects/${projectId}/extract/jobs/${jobId}/cancel`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
    } catch (err) {
      console.error('Error canceling job:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8 bg-gray-900 rounded-lg">
        <div className="text-white">Loading jobs...</div>
      </div>
    );
  }

  const runningJobs = jobs.filter(j => j.status === 'running' || j.status === 'pending');
  const completedJobs = jobs.filter(j => j.status === 'completed');
  const failedJobs = jobs.filter(j => j.status === 'failed');

  return (
    <div className="extraction-job-monitor bg-gray-900 text-white p-6 rounded-lg space-y-6">
      <h2 className="text-2xl font-bold">Extraction Jobs</h2>

      {/* Running jobs */}
      {runningJobs.length > 0 && (
        <div className="job-section">
          <h3 className="text-xl font-semibold mb-4">In Progress ({runningJobs.length})</h3>
          <div className="space-y-3">
            {runningJobs.map(job => (
              <div key={job.id} className="bg-gray-800 p-4 rounded-lg border border-yellow-500">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-400">Scene {job.scene_id}</span>
                    <span className="px-2 py-1 bg-blue-600 rounded text-xs font-medium">
                      {job.extractor_type.toUpperCase()}
                    </span>
                    {job.model_name && (
                      <span className="px-2 py-1 bg-purple-600 rounded text-xs font-medium">
                        {job.model_name}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => cancelJob(job.id)}
                    className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs transition-colors"
                  >
                    Cancel
                  </button>
                </div>

                <div className="mb-2">
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-yellow-500 h-full transition-all duration-300"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{job.progress}%</div>
                </div>

                <div className="text-xs text-gray-400">
                  Started {new Date(job.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed jobs */}
      {completedJobs.length > 0 && (
        <div className="job-section">
          <h3 className="text-xl font-semibold mb-4">Completed ({completedJobs.length})</h3>
          <div className="space-y-3">
            {completedJobs.slice(0, 10).map(job => (
              <div key={job.id} className="bg-gray-800 p-4 rounded-lg border border-green-500">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-400">Scene {job.scene_id}</span>
                    <span className="px-2 py-1 bg-blue-600 rounded text-xs font-medium">
                      {job.extractor_type.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-green-400 text-sm">✓ Complete</span>
                </div>

                <div className="flex items-center gap-4 text-sm mb-2">
                  <span className="text-gray-300">{job.entities_found} entities</span>
                  <span className="text-gray-300">{job.relationships_found} relationships</span>
                  {job.cost > 0 && (
                    <span className="text-yellow-400">${job.cost.toFixed(4)}</span>
                  )}
                </div>

                <div className="text-xs text-gray-400">
                  Completed {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'recently'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Failed jobs */}
      {failedJobs.length > 0 && (
        <div className="job-section">
          <h3 className="text-xl font-semibold mb-4">Failed ({failedJobs.length})</h3>
          <div className="space-y-3">
            {failedJobs.slice(0, 5).map(job => (
              <div key={job.id} className="bg-gray-800 p-4 rounded-lg border border-red-500">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-400">Scene {job.scene_id}</span>
                    <span className="px-2 py-1 bg-blue-600 rounded text-xs font-medium">
                      {job.extractor_type.toUpperCase()}
                    </span>
                  </div>
                  <span className="text-red-400 text-sm">✗ Failed</span>
                </div>

                <div className="text-sm text-red-300 mb-2">
                  Error: {job.error || 'Unknown error'}
                </div>

                <div className="text-xs text-gray-400">
                  Failed {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'recently'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {jobs.length === 0 && (
        <div className="text-center py-8 text-gray-400">
          <div className="text-4xl mb-2">📊</div>
          <p>No extraction jobs yet</p>
          <p className="text-sm mt-1">Jobs will appear here when you extract entities from scenes</p>
        </div>
      )}
    </div>
  );
};

export default ExtractionJobMonitor;
