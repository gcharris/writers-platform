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
