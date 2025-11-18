/**
 * WebSocket Hook for Knowledge Graph Updates
 * Manages WebSocket connections for real-time graph updates
 */

import { useEffect, useRef, useState, useCallback } from 'react';

interface GraphUpdate {
  type: 'entity_added' | 'entity_updated' | 'entity_deleted' |
        'relationship_added' | 'relationship_updated' | 'relationship_deleted' |
        'extraction_started' | 'extraction_progress' | 'extraction_completed' | 'extraction_failed';
  data: any;
  timestamp: string;
}

interface UseKnowledgeGraphWebSocketOptions {
  projectId: string;
  onUpdate?: (update: GraphUpdate) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export const useKnowledgeGraphWebSocket = ({
  projectId,
  onUpdate,
  autoReconnect = true,
  reconnectInterval = 5000,
}: UseKnowledgeGraphWebSocketOptions) => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      const token = localStorage.getItem('auth_token');
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/knowledge-graph/projects/${projectId}/stream?token=${token}`;

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('Knowledge graph WebSocket connected');
        setConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const update: GraphUpdate = JSON.parse(event.data);
          if (onUpdate) {
            onUpdate(update);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('Knowledge graph WebSocket disconnected');
        setConnected(false);
        wsRef.current = null;

        // Auto-reconnect
        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, [projectId, onUpdate, autoReconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Connect on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connected,
    error,
    reconnect: connect,
    disconnect,
  };
};
