/**
 * Auto-Extraction Hook
 * Automatically trigger knowledge graph extraction when scenes are saved
 */

import { useCallback, useEffect, useRef } from 'react';

interface UseAutoExtractionOptions {
  projectId: string;
  enabled: boolean;
  extractorType?: 'llm' | 'ner';
  modelName?: string;
  onExtractionStart?: (jobId: string) => void;
  onExtractionComplete?: () => void;
}

export const useAutoExtraction = ({
  projectId,
  enabled,
  extractorType = 'ner',  // Default to free NER extraction
  modelName = 'claude-sonnet-4.5',
  onExtractionStart,
  onExtractionComplete,
}: UseAutoExtractionOptions) => {
  // Track active polling intervals to clean up on unmount
  const activeIntervalsRef = useRef<Set<NodeJS.Timeout>>(new Set());

  // Cleanup all intervals on unmount
  useEffect(() => {
    return () => {
      activeIntervalsRef.current.forEach(interval => clearInterval(interval));
      activeIntervalsRef.current.clear();
    };
  }, []);

  // Trigger extraction for a scene
  const extractFromScene = useCallback(async (sceneId: string, sceneContent: string) => {
    if (!enabled) return;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `/api/knowledge-graph/projects/${projectId}/extract`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scene_id: sceneId,
            scene_content: sceneContent,
            extractor_type: extractorType,
            model_name: extractorType === 'llm' ? modelName : undefined,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Extraction request failed');
      }

      const data = await response.json();

      if (onExtractionStart) {
        onExtractionStart(data.job_id);
      }

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(
          `/api/knowledge-graph/projects/${projectId}/extract/jobs/${data.job_id}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!statusResponse.ok) {
          clearInterval(pollInterval);
          activeIntervalsRef.current.delete(pollInterval);
          return;
        }

        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          clearInterval(pollInterval);
          activeIntervalsRef.current.delete(pollInterval);
          if (onExtractionComplete) {
            onExtractionComplete();
          }
        } else if (statusData.status === 'failed') {
          clearInterval(pollInterval);
          activeIntervalsRef.current.delete(pollInterval);
          console.error('Extraction failed:', statusData.error);
        }
      }, 2000);  // Poll every 2 seconds

      // Track interval for cleanup
      activeIntervalsRef.current.add(pollInterval);

    } catch (err) {
      console.error('Auto-extraction failed:', err);
    }
  }, [projectId, enabled, extractorType, modelName, onExtractionStart, onExtractionComplete]);

  return {
    extractFromScene,
  };
};
