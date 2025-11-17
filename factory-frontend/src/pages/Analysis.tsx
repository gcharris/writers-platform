import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { projectsApi, analysisApi } from '../api/factory';
import type { AnalysisRequest } from '../types';
import {
  ArrowLeftIcon,
  BeakerIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';

export default function Analysis() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('project');
  const [sceneOutline, setSceneOutline] = useState('');
  const [chapter, setChapter] = useState('');
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [synthesize, setSynthesize] = useState(true);
  const [jobId, setJobId] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);

  // Fetch project
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId,
  });

  // Fetch available models
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: analysisApi.getModels,
  });

  // Fetch analysis status (when job is running)
  const { data: analysisStatus } = useQuery({
    queryKey: ['analysis-status', jobId],
    queryFn: () => analysisApi.getStatus(jobId!),
    enabled: !!jobId && pollingInterval !== null,
    refetchInterval: pollingInterval || false,
  });

  // Fetch analysis results (when complete)
  const { data: analysisResults } = useQuery({
    queryKey: ['analysis-results', jobId],
    queryFn: () => analysisApi.getResults(jobId!),
    enabled: !!jobId && analysisStatus?.status === 'completed',
  });

  // Run analysis mutation
  const runAnalysisMutation = useMutation({
    mutationFn: async (request: AnalysisRequest) => {
      if (!projectId) throw new Error('No project selected');
      return analysisApi.run(projectId, request);
    },
    onSuccess: (data) => {
      setJobId(data.job_id);
      setPollingInterval(3000); // Poll every 3 seconds
    },
  });

  // Stop polling when analysis is complete or failed
  useEffect(() => {
    if (analysisStatus?.status === 'completed' || analysisStatus?.status === 'failed') {
      setPollingInterval(null);
    }
  }, [analysisStatus?.status]);

  // Initialize with default agents
  useEffect(() => {
    if (modelsData && selectedAgents.length === 0) {
      setSelectedAgents(modelsData.default);
    }
  }, [modelsData, selectedAgents]);

  const handleStartAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    await runAnalysisMutation.mutateAsync({
      scene_outline: sceneOutline,
      chapter: chapter || undefined,
      agents: selectedAgents,
      synthesize,
    });
  };

  const toggleAgent = (agentId: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agentId)
        ? prev.filter((id) => id !== agentId)
        : [...prev, agentId]
    );
  };

  if (!projectId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No project selected</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 text-indigo-600 hover:text-indigo-700"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Show results view if analysis is complete
  if (analysisResults && analysisStatus?.status === 'completed') {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => navigate(`/editor/${projectId}`)}
              className="text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
            >
              <ArrowLeftIcon className="h-5 w-5" />
              Back to Editor
            </button>
            <div className="flex items-center gap-3">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Analysis Complete</h1>
                <p className="text-gray-600">{project?.title}</p>
              </div>
            </div>
          </div>

          {/* Summary cards */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <p className="text-sm text-gray-600 mb-1">Best Score</p>
              <p className="text-3xl font-bold text-indigo-600">
                {analysisResults.summary?.best_score?.toFixed(1) || 'N/A'}/70
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {analysisResults.summary?.best_agent}
              </p>
            </div>

            {analysisResults.summary?.hybrid_score && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <p className="text-sm text-gray-600 mb-1">Hybrid Score</p>
                <p className="text-3xl font-bold text-purple-600">
                  {analysisResults.summary.hybrid_score.toFixed(1)}/70
                </p>
                <p className="text-xs text-gray-500 mt-1">Synthesized version</p>
              </div>
            )}

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <p className="text-sm text-gray-600 mb-1">Total Cost</p>
              <p className="text-3xl font-bold text-gray-900">
                ${analysisResults.summary?.total_cost?.toFixed(3) || '0.00'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {analysisResults.summary?.total_tokens?.toLocaleString()} tokens
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <p className="text-sm text-gray-600 mb-1">Time</p>
              <p className="text-3xl font-bold text-gray-900">
                {(() => {
                  const start = new Date(analysisResults.started_at!);
                  const end = new Date(analysisResults.completed_at!);
                  const seconds = Math.floor((end.getTime() - start.getTime()) / 1000);
                  return seconds < 60 ? `${seconds}s` : `${Math.floor(seconds / 60)}m`;
                })()}
              </p>
              <p className="text-xs text-gray-500 mt-1">Processing time</p>
            </div>
          </div>

          {/* Full results */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Detailed Results</h2>

            <div className="prose max-w-none">
              <pre className="bg-gray-50 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(analysisResults.full_results, null, 2)}
              </pre>
            </div>

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => {
                  setJobId(null);
                  setSceneOutline('');
                  setChapter('');
                }}
                className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Run New Analysis
              </button>
              <button
                onClick={() => navigate(`/editor/${projectId}`)}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Back to Editor
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show progress view if analysis is running
  if (jobId && analysisStatus) {
    const getStatusIcon = () => {
      switch (analysisStatus.status) {
        case 'completed':
          return <CheckCircleIcon className="h-12 w-12 text-green-600" />;
        case 'failed':
          return <XCircleIcon className="h-12 w-12 text-red-600" />;
        case 'running':
          return <BeakerIcon className="h-12 w-12 text-indigo-600 animate-pulse" />;
        default:
          return <ClockIcon className="h-12 w-12 text-gray-400" />;
      }
    };

    const getStatusText = () => {
      switch (analysisStatus.status) {
        case 'pending':
          return 'Analysis queued...';
        case 'running':
          return 'Running AI analysis...';
        case 'completed':
          return 'Analysis complete!';
        case 'failed':
          return 'Analysis failed';
        default:
          return 'Processing...';
      }
    };

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
          <div className="text-center">
            <div className="mb-4">{getStatusIcon()}</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {getStatusText()}
            </h2>
            {analysisStatus.scene_outline && (
              <p className="text-gray-600 mb-4">{analysisStatus.scene_outline}</p>
            )}
            {analysisStatus.status === 'running' && (
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div className="bg-indigo-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
                </div>
                <p className="text-sm text-gray-500">
                  This may take a few minutes...
                </p>
              </div>
            )}
            {analysisStatus.status === 'failed' && analysisStatus.error_message && (
              <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {analysisStatus.error_message}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Show analysis configuration form
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/editor/${projectId}`)}
            className="text-gray-600 hover:text-gray-900 mb-4 flex items-center gap-2"
          >
            <ArrowLeftIcon className="h-5 w-5" />
            Back to Editor
          </button>
          <h1 className="text-3xl font-bold text-gray-900">AI Analysis</h1>
          <p className="text-gray-600 mt-1">{project?.title}</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <form onSubmit={handleStartAnalysis} className="space-y-6">
            {/* Scene outline */}
            <div>
              <label htmlFor="outline" className="block text-sm font-medium text-gray-700 mb-2">
                Scene Outline *
              </label>
              <textarea
                id="outline"
                required
                value={sceneOutline}
                onChange={(e) => setSceneOutline(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Describe the scene you want to analyze or generate..."
              />
              <p className="mt-1 text-sm text-gray-500">
                Provide a brief description of what happens in this scene
              </p>
            </div>

            {/* Chapter identifier */}
            <div>
              <label htmlFor="chapter" className="block text-sm font-medium text-gray-700 mb-2">
                Chapter/Scene Number
              </label>
              <input
                id="chapter"
                type="text"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="e.g., 2.3.6 or Chapter 5"
              />
            </div>

            {/* AI Models selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Models
              </label>
              <div className="space-y-2">
                {modelsData?.models.map((model) => (
                  <label
                    key={model.id}
                    className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedAgents.includes(model.id)}
                      onChange={() => toggleAgent(model.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{model.name}</p>
                      <p className="text-sm text-gray-600">{model.description}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        ${model.cost_per_1k_tokens}/1k tokens
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Synthesize option */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="synthesize"
                checked={synthesize}
                onChange={(e) => setSynthesize(e.target.checked)}
                className="mt-1"
              />
              <div>
                <label htmlFor="synthesize" className="block text-sm font-medium text-gray-700">
                  Generate hybrid synthesis
                </label>
                <p className="text-sm text-gray-500">
                  Combine the best elements from all variations into a new version
                </p>
              </div>
            </div>

            {/* Error display */}
            {runAnalysisMutation.isError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                Failed to start analysis. Please try again.
              </div>
            )}

            {/* Submit */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => navigate(`/editor/${projectId}`)}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={runAnalysisMutation.isPending || selectedAgents.length === 0}
                className="flex-1 inline-flex items-center justify-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <BeakerIcon className="h-5 w-5 mr-2" />
                {runAnalysisMutation.isPending ? 'Starting...' : 'Run Analysis'}
              </button>
            </div>
          </form>
        </div>

        {/* Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-medium text-blue-900 mb-2">How it works</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Multiple AI models will analyze your scene simultaneously</li>
            <li>• Each model will be scored across 7 dimensions (voice, pacing, etc.)</li>
            <li>• Models will critique each other's work</li>
            <li>• The best elements will be synthesized into a hybrid version</li>
            <li>• Typical analysis takes 2-5 minutes</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
