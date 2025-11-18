import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../api/factory';
import type { Scene } from '../types';
import { MarkdownEditor } from '../components/editor/MarkdownEditor';
import {
  ArrowLeftIcon,
  BeakerIcon,
  PlusIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

export default function Editor() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [selectedSceneId, setSelectedSceneId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Fetch project
  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId,
  });

  // Fetch scenes
  const { data: scenes, isLoading: scenesLoading } = useQuery({
    queryKey: ['scenes', projectId],
    queryFn: () => projectsApi.getScenes(projectId!),
    enabled: !!projectId,
  });

  // Select first scene by default
  useEffect(() => {
    if (scenes && scenes.length > 0 && !selectedSceneId) {
      setSelectedSceneId(scenes[0].id);
      setEditingContent(scenes[0].content);
    }
  }, [scenes, selectedSceneId]);

  // Update editing content when scene changes
  useEffect(() => {
    if (selectedSceneId && scenes) {
      const scene = scenes.find((s: Scene) => s.id === selectedSceneId);
      if (scene) {
        setEditingContent(scene.content);
        setHasUnsavedChanges(false);
      }
    }
  }, [selectedSceneId, scenes]);

  const handleContentChange = (value: string) => {
    setEditingContent(value);
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    // In a real implementation, this would update the scene via API
    // For now, we'll just clear the unsaved changes flag
    setHasUnsavedChanges(false);
    // TODO: Implement scene update API
  };

  const selectedScene = scenes?.find((s: Scene) => s.id === selectedSceneId);
  const wordCount = editingContent.split(/\s+/).filter(Boolean).length;

  if (projectLoading || scenesLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Project not found</p>
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                <ArrowLeftIcon className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{project.title}</h1>
                <p className="text-sm text-gray-500">
                  {project.word_count.toLocaleString()} words • {project.scene_count} scenes
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {hasUnsavedChanges && (
                <span className="text-sm text-amber-600">Unsaved changes</span>
              )}
              <button
                onClick={handleSave}
                disabled={!hasUnsavedChanges}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save
              </button>
              <button
                onClick={() => navigate(`/analysis?project=${projectId}`)}
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <BeakerIcon className="h-5 w-5 mr-2" />
                Analyze
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-5rem)]">
        {/* Sidebar - Scene list */}
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-gray-900">Scenes</h2>
              <button className="p-1 text-gray-400 hover:text-gray-600">
                <PlusIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-1">
              {scenes && scenes.length > 0 ? (
                scenes.map((scene: Scene) => (
                  <button
                    key={scene.id}
                    onClick={() => setSelectedSceneId(scene.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      selectedSceneId === scene.id
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-sm">
                      {scene.title || `Scene ${scene.sequence}`}
                    </div>
                    {scene.chapter_number && (
                      <div className="text-xs text-gray-500">
                        Chapter {scene.chapter_number}
                        {scene.scene_number && `.${scene.scene_number}`}
                      </div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      {scene.word_count.toLocaleString()} words
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <DocumentTextIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No scenes yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main editor */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {selectedScene ? (
            <>
              {/* Scene header */}
              <div className="bg-white border-b border-gray-200 px-8 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {selectedScene.title || `Scene ${selectedScene.sequence}`}
                    </h3>
                    {selectedScene.chapter_number && (
                      <p className="text-sm text-gray-500">
                        Chapter {selectedScene.chapter_number}
                        {selectedScene.scene_number && `.${selectedScene.scene_number}`}
                      </p>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    {wordCount.toLocaleString()} words
                  </div>
                </div>
              </div>

              {/* Editor */}
              <div className="flex-1 overflow-hidden bg-white">
                <MarkdownEditor
                  content={editingContent}
                  onChange={handleContentChange}
                  onSave={handleSave}
                  placeholder="Start writing your story..."
                  autoSave={true}
                  autoSaveDelay={2000}
                  copilotEnabled={true}
                  projectId={projectId}
                  sceneId={selectedSceneId || undefined}
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <DocumentTextIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p>Select a scene to start editing</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
