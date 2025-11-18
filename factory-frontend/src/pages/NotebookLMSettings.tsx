/**
 * NotebookLM Settings Page
 *
 * Allows writers to configure NotebookLM notebook URLs for their project.
 * Phase 9: NotebookLM MCP Integration
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

interface NotebookLMSettingsProps {
  projectId?: string;
}

export const NotebookLMSettings: React.FC<NotebookLMSettingsProps> = ({ projectId: propProjectId }) => {
  const { projectId: paramProjectId } = useParams();
  const projectId = propProjectId || paramProjectId;
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ available: boolean; message: string } | null>(null);

  const [urls, setUrls] = useState({
    character_research: '',
    world_building: '',
    themes: ''
  });

  const [autoQuery, setAutoQuery] = useState(true);

  // Batch extraction state
  const [extracting, setExtracting] = useState(false);
  const [extractTypes, setExtractTypes] = useState({
    character: true,
    world: true,
    themes: true
  });
  const [batchResults, setBatchResults] = useState<any>(null);

  useEffect(() => {
    if (projectId) {
      loadCurrentSettings();
      checkMCPStatus();
    }
  }, [projectId]);

  const loadCurrentSettings = async () => {
    try {
      const response = await fetch(`/api/notebooklm/projects/${projectId}/notebooks`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.notebooks) {
          setUrls({
            character_research: data.notebooks.character_research || '',
            world_building: data.notebooks.world_building || '',
            themes: data.notebooks.themes || ''
          });
        }
        if (data.config) {
          setAutoQuery(data.config.auto_query_on_copilot !== false);
        }
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkMCPStatus = async () => {
    try {
      const response = await fetch('/api/notebooklm/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Error checking MCP status:', error);
      setStatus({ available: false, message: 'MCP server not reachable' });
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      const params = new URLSearchParams();
      if (urls.character_research) params.append('character_research_url', urls.character_research);
      if (urls.world_building) params.append('world_building_url', urls.world_building);
      if (urls.themes) params.append('themes_url', urls.themes);
      params.append('auto_query_on_copilot', String(autoQuery));

      const response = await fetch(`/api/notebooklm/projects/${projectId}/configure?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        alert('NotebookLM configuration saved successfully!');
      } else {
        alert('Failed to save configuration');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleBatchExtract = async () => {
    setExtracting(true);
    setBatchResults(null);

    try {
      const params = new URLSearchParams();
      params.append('project_ids', projectId!);

      // Add extract types
      if (extractTypes.character) params.append('extract_types', 'character');
      if (extractTypes.world) params.append('extract_types', 'world');
      if (extractTypes.themes) params.append('extract_types', 'themes');

      const response = await fetch(`/api/notebooklm/batch-extract?${params.toString()}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const results = await response.json();
        setBatchResults(results);
      } else {
        alert('Failed to extract NotebookLM data');
      }
    } catch (error) {
      console.error('Error during batch extraction:', error);
      alert('Error during batch extraction');
    } finally {
      setExtracting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          NotebookLM Integration
        </h1>
        <p className="text-gray-400">
          Connect your NotebookLM research notebooks to enhance AI-powered writing assistance
        </p>
      </div>

      {/* MCP Status */}
      {status && (
        <div className={`mb-6 p-4 rounded border ${
          status.available
            ? 'bg-green-900/20 border-green-700'
            : 'bg-yellow-900/20 border-yellow-700'
        }`}>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              status.available ? 'bg-green-500' : 'bg-yellow-500'
            }`} />
            <span className={status.available ? 'text-green-400' : 'text-yellow-400'}>
              {status.message}
            </span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mb-6 p-4 bg-blue-900/20 border border-blue-800 rounded">
        <h3 className="font-semibold text-blue-300 mb-2">
          How It Works
        </h3>
        <ol className="text-sm text-blue-200 space-y-1 list-decimal list-inside">
          <li>Create NotebookLM notebooks externally at notebooklm.google.com</li>
          <li>Add your research sources (YouTube videos, PDFs, articles) to each notebook</li>
          <li>Copy the notebook URLs and paste them below</li>
          <li>AI copilot will automatically query your research while you write</li>
        </ol>
      </div>

      {/* Notebook URL Inputs */}
      <div className="space-y-6">
        {/* Character Research */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Character Research Notebook (Optional)
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Interviews, personality studies, voice examples for character inspiration
          </p>
          <input
            type="url"
            value={urls.character_research}
            onChange={(e) => setUrls({ ...urls, character_research: e.target.value })}
            placeholder="https://notebooklm.google.com/notebook/..."
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* World Building */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            World Building Notebook (Optional)
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Future tech, social trends, setting research, world details
          </p>
          <input
            type="url"
            value={urls.world_building}
            onChange={(e) => setUrls({ ...urls, world_building: e.target.value })}
            placeholder="https://notebooklm.google.com/notebook/..."
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Themes & Philosophy */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Themes & Philosophy Notebook (Optional)
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Ethical frameworks, philosophical concepts, story themes
          </p>
          <input
            type="url"
            value={urls.themes}
            onChange={(e) => setUrls({ ...urls, themes: e.target.value })}
            placeholder="https://notebooklm.google.com/notebook/..."
            className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Auto-query Setting */}
        <div className="flex items-start gap-3 p-4 bg-gray-800 rounded border border-gray-700">
          <input
            type="checkbox"
            id="auto-query"
            checked={autoQuery}
            onChange={(e) => setAutoQuery(e.target.checked)}
            className="mt-1"
          />
          <div className="flex-1">
            <label htmlFor="auto-query" className="block text-sm font-medium text-gray-300 mb-1">
              Enable AI Copilot Integration
            </label>
            <p className="text-xs text-gray-500">
              Automatically query NotebookLM notebooks while writing to ground AI suggestions in your research.
              Queries are triggered when you mention characters, locations, or concepts from your knowledge graph.
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-8 flex gap-4">
        <button
          onClick={handleSave}
          disabled={saving || (!urls.character_research && !urls.world_building && !urls.themes)}
          className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
        <button
          onClick={() => navigate(-1)}
          className="px-6 py-3 bg-gray-700 text-white rounded hover:bg-gray-600"
        >
          Cancel
        </button>
      </div>

      {/* 🚀 BATCH EXTRACTION Section */}
      {(urls.character_research || urls.world_building || urls.themes) && (
        <div className="mt-8 p-6 bg-gradient-to-br from-purple-900/30 to-blue-900/30 border border-purple-700 rounded-lg">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-purple-300 mb-2">
              🚀 Batch Extraction
            </h2>
            <p className="text-sm text-gray-400">
              Extract research from all configured NotebookLM notebooks into your Knowledge Graph at once.
              This is faster than extracting one notebook at a time.
            </p>
          </div>

          {/* Extract Type Checkboxes */}
          <div className="mb-4 space-y-2">
            <p className="text-sm font-medium text-gray-300 mb-2">What to extract:</p>
            <div className="flex flex-wrap gap-4">
              {urls.character_research && (
                <label className="flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={extractTypes.character}
                    onChange={(e) => setExtractTypes({ ...extractTypes, character: e.target.checked })}
                  />
                  Character Research
                </label>
              )}
              {urls.world_building && (
                <label className="flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={extractTypes.world}
                    onChange={(e) => setExtractTypes({ ...extractTypes, world: e.target.checked })}
                  />
                  World Building
                </label>
              )}
              {urls.themes && (
                <label className="flex items-center gap-2 text-sm text-gray-300">
                  <input
                    type="checkbox"
                    checked={extractTypes.themes}
                    onChange={(e) => setExtractTypes({ ...extractTypes, themes: e.target.checked })}
                  />
                  Themes & Philosophy
                </label>
              )}
            </div>
          </div>

          {/* Extract Button */}
          <button
            onClick={handleBatchExtract}
            disabled={extracting || (!extractTypes.character && !extractTypes.world && !extractTypes.themes)}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {extracting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Extracting...
              </>
            ) : (
              '⚡ Start Batch Extraction'
            )}
          </button>

          {/* Batch Results */}
          {batchResults && (
            <div className="mt-4 p-4 bg-gray-900/50 rounded border border-gray-700">
              <h3 className="font-semibold text-green-400 mb-2">
                ✅ Extraction Complete!
              </h3>
              <div className="text-sm text-gray-300 space-y-1">
                <p>• Projects processed: {batchResults.total_projects}</p>
                <p>• Successful: {batchResults.success_count}</p>
                <p>• Entities added: {batchResults.total_entities_added}</p>
                <p>• Entities enriched: {batchResults.total_entities_enriched}</p>
                {batchResults.error_count > 0 && (
                  <p className="text-red-400">• Errors: {batchResults.error_count}</p>
                )}
              </div>

              {/* Per-project results */}
              {batchResults.project_results && batchResults.project_results.length > 0 && (
                <div className="mt-3 space-y-2">
                  {batchResults.project_results.map((result: any, index: number) => (
                    <div key={index} className="text-xs p-2 bg-gray-800 rounded">
                      <p className="font-semibold text-gray-300">{result.project_title}</p>
                      <p className="text-gray-400">
                        Status: {result.status} | Added: {result.entities_added} | Enriched: {result.entities_enriched}
                      </p>
                      {result.errors && result.errors.length > 0 && (
                        <p className="text-red-400 mt-1">Errors: {result.errors.join(', ')}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-8 p-4 bg-gray-900 rounded border border-gray-800">
        <h4 className="font-semibold text-gray-300 mb-2">
          💡 Tips
        </h4>
        <ul className="text-sm text-gray-400 space-y-1 list-disc list-inside">
          <li>You can add notebooks later - they're all optional</li>
          <li>The AI will only query notebooks when relevant entities are mentioned</li>
          <li>Research context is limited to 300 characters to keep copilot responses fast</li>
          <li>You can update notebook URLs anytime in Project Settings</li>
        </ul>
      </div>
    </div>
  );
};

export default NotebookLMSettings;
