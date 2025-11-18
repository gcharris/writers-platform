/**
 * Scene Editor with Knowledge Graph Integration
 * Enhanced scene editor with integrated knowledge graph sidebar and auto-extraction
 */

import React, { useState, useEffect } from 'react';
import { Entity } from '../../types/knowledge-graph';
import { useAutoExtraction } from '../../hooks/useAutoExtraction';
import { GraphVisualization } from '../knowledge-graph/GraphVisualization';
import { EntityBrowser } from '../knowledge-graph/EntityBrowser';

interface SceneEditorWithKnowledgeGraphProps {
  projectId: string;
  sceneId: string;
  initialContent: string;
  onSave: (content: string) => Promise<void>;
}

export const SceneEditorWithKnowledgeGraph: React.FC<SceneEditorWithKnowledgeGraphProps> = ({
  projectId,
  sceneId,
  initialContent,
  onSave,
}) => {
  const [content, setContent] = useState(initialContent);
  const [saving, setSaving] = useState(false);
  const [autoExtractEnabled, setAutoExtractEnabled] = useState(true);
  const [extractorType, setExtractorType] = useState<'llm' | 'ner'>('ner');
  const [showKnowledgePanel, setShowKnowledgePanel] = useState(true);
  const [highlightedEntities, setHighlightedEntities] = useState<string[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [activeTab, setActiveTab] = useState<'graph' | 'entities' | 'context'>('graph');

  const { extractFromScene } = useAutoExtraction({
    projectId,
    enabled: autoExtractEnabled,
    extractorType,
    onExtractionStart: (jobId) => {
      console.log('Extraction started:', jobId);
    },
    onExtractionComplete: () => {
      console.log('Extraction completed');
    },
  });

  // Save scene and trigger extraction
  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(content);

      // Trigger extraction if enabled
      if (autoExtractEnabled) {
        await extractFromScene(sceneId, content);
      }
    } catch (err) {
      console.error('Save failed:', err);
      alert('Failed to save scene');
    } finally {
      setSaving(false);
    }
  };

  // Highlight entities mentioned in the scene
  useEffect(() => {
    // Find entity names mentioned in content
    const findMentionedEntities = async () => {
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

        if (!response.ok) return;

        const data = await response.json();
        const mentioned = data
          .filter((entity: any) => content.toLowerCase().includes(entity.name.toLowerCase()))
          .map((entity: any) => entity.id);

        setHighlightedEntities(mentioned);
      } catch (err) {
        console.error('Error finding mentioned entities:', err);
      }
    };

    findMentionedEntities();
  }, [content, projectId]);

  return (
    <div className="scene-editor-with-knowledge-graph flex gap-4 h-full bg-gray-950 text-white">
      {/* Main editor */}
      <div className="editor-main flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="editor-toolbar bg-gray-900 p-4 border-b border-gray-700 flex items-center justify-between gap-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
          >
            {saving ? 'Saving...' : 'Save Scene'}
          </button>

          <div className="extraction-controls flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoExtractEnabled}
                onChange={(e) => setAutoExtractEnabled(e.target.checked)}
                className="rounded"
              />
              Auto-extract entities
            </label>

            <select
              value={extractorType}
              onChange={(e) => setExtractorType(e.target.value as 'llm' | 'ner')}
              disabled={!autoExtractEnabled}
              className="px-3 py-1 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ner">Fast (NER - Free)</option>
              <option value="llm">High Quality (AI - Paid)</option>
            </select>
          </div>

          <button
            onClick={() => setShowKnowledgePanel(!showKnowledgePanel)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
          >
            {showKnowledgePanel ? 'Hide' : 'Show'} Knowledge Graph
          </button>
        </div>

        {/* Text editor */}
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="scene-content-editor flex-1 p-6 bg-gray-900 text-white focus:outline-none resize-none font-mono"
          placeholder="Write your scene here..."
        />

        {/* Footer */}
        <div className="editor-footer bg-gray-900 px-6 py-3 border-t border-gray-700 flex items-center justify-between text-sm text-gray-400">
          <span className="word-count">
            {content.split(/\s+/).filter(w => w.length > 0).length} words
          </span>
          {highlightedEntities.length > 0 && (
            <span className="mentioned-entities">
              {highlightedEntities.length} entities mentioned
            </span>
          )}
        </div>
      </div>

      {/* Knowledge graph sidebar */}
      {showKnowledgePanel && (
        <div className="knowledge-panel w-96 bg-gray-900 flex flex-col border-l border-gray-700">
          {/* Panel tabs */}
          <div className="panel-tabs flex border-b border-gray-700">
            <button
              onClick={() => setActiveTab('graph')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'graph'
                  ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Graph
            </button>
            <button
              onClick={() => setActiveTab('entities')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'entities'
                  ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Entities
            </button>
            <button
              onClick={() => setActiveTab('context')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'context'
                  ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Context
            </button>
          </div>

          {/* Panel content */}
          <div className="panel-content flex-1 overflow-auto">
            {activeTab === 'graph' && (
              <div className="mini-graph p-4">
                <h3 className="text-lg font-semibold mb-4">Scene Graph</h3>
                <GraphVisualization
                  projectId={projectId}
                  highlightEntities={highlightedEntities}
                  height={300}
                  onEntityClick={(entity) => setSelectedEntity(entity)}
                />
              </div>
            )}

            {activeTab === 'entities' && (
              <div className="entity-sidebar h-full">
                <EntityBrowser
                  projectId={projectId}
                  onEntitySelect={(entity) => setSelectedEntity(entity)}
                  selectedEntityId={selectedEntity?.id}
                />
              </div>
            )}

            {activeTab === 'context' && (
              <div className="context-panel p-4">
                <h3 className="text-lg font-semibold mb-4">Scene Context</h3>
                {selectedEntity ? (
                  <div className="selected-entity-info bg-gray-800 p-4 rounded-lg">
                    <h4 className="text-xl font-bold mb-2">{selectedEntity.name}</h4>
                    <p className="text-sm text-gray-400 mb-3 capitalize">{selectedEntity.type}</p>
                    {selectedEntity.description && (
                      <p className="text-sm text-gray-300 mb-3">
                        {selectedEntity.description}
                      </p>
                    )}
                    {selectedEntity.aliases && selectedEntity.aliases.length > 0 && (
                      <div className="mb-2">
                        <span className="text-xs text-gray-400">Aliases: </span>
                        <span className="text-sm text-gray-300">{selectedEntity.aliases.join(', ')}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center text-gray-400 py-8">
                    <div className="text-4xl mb-2">🔍</div>
                    <p>Select an entity to view context</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SceneEditorWithKnowledgeGraph;
