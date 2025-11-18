/**
 * Reference File with Auto-Linking
 * Automatically link reference files to knowledge graph entities
 */

import React, { useState, useEffect } from 'react';
import { Entity, EntityType } from '../../types/knowledge-graph';

interface ReferenceFileWithAutoLinkProps {
  projectId: string;
  fileId: string;
  content: string;
  onSave: (content: string, linkedEntities: string[]) => Promise<void>;
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

export const ReferenceFileWithAutoLink: React.FC<ReferenceFileWithAutoLinkProps> = ({
  projectId,
  fileId,
  content,
  onSave,
}) => {
  const [editedContent, setEditedContent] = useState(content);
  const [linkedEntities, setLinkedEntities] = useState<Entity[]>([]);
  const [suggestedEntities, setSuggestedEntities] = useState<Entity[]>([]);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  // Find entities mentioned in content
  useEffect(() => {
    const findLinkedEntities = async () => {
      setLoading(true);
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

        // Find entities mentioned in content
        const mentioned = data.filter((entity: Entity) =>
          editedContent.toLowerCase().includes(entity.name.toLowerCase())
        );

        setLinkedEntities(mentioned);

        // Suggest related entities (characters and important concepts)
        const suggested = data.filter((entity: Entity) =>
          !mentioned.includes(entity) &&
          (entity.type === 'character' || entity.type === 'concept')
        );

        setSuggestedEntities(suggested.slice(0, 5));
      } catch (err) {
        console.error('Error finding linked entities:', err);
      } finally {
        setLoading(false);
      }
    };

    findLinkedEntities();
  }, [editedContent, projectId]);

  // Save with linked entities
  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(editedContent, linkedEntities.map(e => e.id));
    } catch (err) {
      console.error('Save failed:', err);
      alert('Failed to save reference file');
    } finally {
      setSaving(false);
    }
  };

  // Add entity mention to content
  const addEntityMention = (entity: Entity) => {
    setEditedContent(prev => `${prev}\n\nRelated: ${entity.name} (${entity.type})`);
  };

  return (
    <div className="reference-file-with-auto-link flex gap-4 h-full bg-gray-950 text-white">
      {/* Editor */}
      <div className="reference-editor flex-1 flex flex-col">
        <div className="editor-toolbar bg-gray-900 p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Reference File</h2>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded transition-colors"
          >
            {saving ? 'Saving...' : 'Save Reference File'}
          </button>
        </div>

        <textarea
          value={editedContent}
          onChange={(e) => setEditedContent(e.target.value)}
          className="reference-content-editor flex-1 p-6 bg-gray-900 text-white focus:outline-none resize-none font-mono"
          placeholder="Add reference material, character notes, world-building details..."
        />

        <div className="editor-footer bg-gray-900 px-6 py-3 border-t border-gray-700 text-sm text-gray-400">
          {editedContent.split(/\s+/).filter(w => w.length > 0).length} words
        </div>
      </div>

      {/* Linked entities sidebar */}
      <div className="linked-entities-sidebar w-80 bg-gray-900 flex flex-col border-l border-gray-700">
        {loading ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            Loading entities...
          </div>
        ) : (
          <>
            {/* Linked entities */}
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold mb-4">
                Linked Entities ({linkedEntities.length})
              </h3>
              {linkedEntities.length === 0 ? (
                <div className="text-center text-gray-400 py-4">
                  <div className="text-3xl mb-2">🔗</div>
                  <p className="text-sm">No entities linked yet</p>
                  <p className="text-xs mt-1">Mention entity names to auto-link</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {linkedEntities.map(entity => (
                    <div
                      key={entity.id}
                      className="bg-gray-800 p-3 rounded-lg flex items-center gap-3"
                    >
                      <span className={`${ENTITY_TYPE_COLORS[entity.type]} w-2 h-2 rounded-full flex-shrink-0`}></span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate">{entity.name}</div>
                        <div className="text-xs text-gray-400 capitalize">{entity.type}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Suggested entities */}
            {suggestedEntities.length > 0 && (
              <div className="p-4 flex-1 overflow-auto">
                <h3 className="text-lg font-semibold mb-4">Suggested Entities</h3>
                <div className="space-y-2">
                  {suggestedEntities.map(entity => (
                    <div
                      key={entity.id}
                      className="bg-gray-800 p-3 rounded-lg hover:bg-gray-750 transition-colors cursor-pointer"
                      onClick={() => addEntityMention(entity)}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`${ENTITY_TYPE_COLORS[entity.type]} w-2 h-2 rounded-full flex-shrink-0`}></span>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{entity.name}</div>
                          <div className="text-xs text-gray-400 capitalize">{entity.type}</div>
                        </div>
                        <button className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                          +
                        </button>
                      </div>
                      {entity.description && (
                        <p className="text-xs text-gray-400 line-clamp-2">
                          {entity.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ReferenceFileWithAutoLink;
