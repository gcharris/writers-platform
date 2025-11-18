/**
 * Export & Import Component
 * Export graph data to GraphML, NotebookLM, and JSON formats
 */

import React, { useState } from 'react';

interface ExportImportProps {
  projectId: string;
}

export const ExportImport: React.FC<ExportImportProps> = ({ projectId }) => {
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  // Export to GraphML
  const exportGraphML = async () => {
    setExporting(true);
    setExportStatus('Exporting to GraphML...');
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/export/graphml`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge-graph-${projectId}.graphml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus('✓ GraphML exported successfully!');
      setTimeout(() => setExportStatus(null), 3000);
    } catch (err) {
      console.error('Export error:', err);
      setExportStatus('✗ Export failed');
      setTimeout(() => setExportStatus(null), 3000);
    } finally {
      setExporting(false);
    }
  };

  // Export to NotebookLM format
  const exportNotebookLM = async () => {
    setExporting(true);
    setExportStatus('Exporting to NotebookLM format...');
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/export/notebooklm`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge-graph-notebooklm-${projectId}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus('✓ NotebookLM file exported successfully!');
      setTimeout(() => setExportStatus(null), 3000);
    } catch (err) {
      console.error('Export error:', err);
      setExportStatus('✗ Export failed');
      setTimeout(() => setExportStatus(null), 3000);
    } finally {
      setExporting(false);
    }
  };

  // Export to JSON
  const exportJSON = async () => {
    setExporting(true);
    setExportStatus('Exporting to JSON...');
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/graph`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `knowledge-graph-${projectId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus('✓ JSON exported successfully!');
      setTimeout(() => setExportStatus(null), 3000);
    } catch (err) {
      console.error('Export error:', err);
      setExportStatus('✗ Export failed');
      setTimeout(() => setExportStatus(null), 3000);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="export-import-panel bg-gray-900 text-white p-6 rounded-lg">
      <h2 className="text-2xl font-bold mb-6">Export & Import</h2>

      {/* Status message */}
      {exportStatus && (
        <div className={`mb-4 p-3 rounded ${exportStatus.startsWith('✓') ? 'bg-green-900 bg-opacity-50 border border-green-500' : 'bg-red-900 bg-opacity-50 border border-red-500'}`}>
          <div className={exportStatus.startsWith('✓') ? 'text-green-300' : 'text-red-300'}>
            {exportStatus}
          </div>
        </div>
      )}

      {/* Export section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-4">Export Knowledge Graph</h3>
        <p className="text-sm text-gray-400 mb-6">
          Export your knowledge graph to various formats for external analysis or backup
        </p>

        <div className="space-y-4">
          {/* GraphML Export */}
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-lg mb-1">GraphML Format</h4>
                <p className="text-sm text-gray-400">
                  Standard graph format for visualization tools like Gephi, Cytoscape, and yEd.
                  Preserves all graph structure and properties.
                </p>
              </div>
            </div>
            <button
              onClick={exportGraphML}
              disabled={exporting}
              className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors w-full md:w-auto"
            >
              {exporting ? 'Exporting...' : 'Export to GraphML'}
            </button>
          </div>

          {/* NotebookLM Export */}
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-lg mb-1">NotebookLM Format</h4>
                <p className="text-sm text-gray-400">
                  Markdown format optimized for Google NotebookLM. Includes character profiles,
                  locations, and key relationships in a readable narrative format.
                </p>
              </div>
            </div>
            <button
              onClick={exportNotebookLM}
              disabled={exporting}
              className="mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded transition-colors w-full md:w-auto"
            >
              {exporting ? 'Exporting...' : 'Export to NotebookLM'}
            </button>
          </div>

          {/* JSON Export */}
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-lg mb-1">JSON Format</h4>
                <p className="text-sm text-gray-400">
                  Raw JSON data containing all nodes, edges, and metadata. Perfect for backup,
                  custom processing, or integration with other tools.
                </p>
              </div>
            </div>
            <button
              onClick={exportJSON}
              disabled={exporting}
              className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded transition-colors w-full md:w-auto"
            >
              {exporting ? 'Exporting...' : 'Export to JSON'}
            </button>
          </div>
        </div>
      </div>

      {/* Import section (placeholder) */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Import Knowledge Graph</h3>
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="text-center text-gray-400">
            <div className="text-4xl mb-2">📥</div>
            <p className="font-semibold mb-2">Import functionality coming soon</p>
            <p className="text-sm">
              Future updates will support importing knowledge graphs from GraphML and JSON formats,
              allowing you to merge or replace existing data.
            </p>
          </div>
        </div>
      </div>

      {/* Export tips */}
      <div className="mt-6 bg-blue-900 bg-opacity-30 border border-blue-500 p-4 rounded-lg">
        <div className="flex items-start gap-3">
          <div className="text-blue-400 text-xl">💡</div>
          <div className="text-sm">
            <div className="font-semibold text-blue-300 mb-1">Export Tips</div>
            <ul className="space-y-1 text-gray-300">
              <li>• Use <strong>GraphML</strong> to visualize your story structure in Gephi</li>
              <li>• Use <strong>NotebookLM</strong> to get AI insights on your characters and plot</li>
              <li>• Use <strong>JSON</strong> for backup or custom data processing</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportImport;
