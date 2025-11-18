/**
 * Live Graph Updates Component
 * Display real-time updates to the knowledge graph
 */

import React, { useState, useEffect } from 'react';
import { useKnowledgeGraphWebSocket } from '../../hooks/useKnowledgeGraphWebSocket';

interface LiveGraphUpdatesProps {
  projectId: string;
  onUpdateReceived?: () => void;  // Callback to refresh graph visualization
}

interface UpdateMessage {
  id: string;
  type: string;
  message: string;
  timestamp: Date;
}

export const LiveGraphUpdates: React.FC<LiveGraphUpdatesProps> = ({
  projectId,
  onUpdateReceived,
}) => {
  const [updates, setUpdates] = useState<UpdateMessage[]>([]);
  const [showNotifications, setShowNotifications] = useState(true);

  const { connected, error } = useKnowledgeGraphWebSocket({
    projectId,
    onUpdate: (update) => {
      // Format update message
      let message = '';
      switch (update.type) {
        case 'entity_added':
          message = `Added entity: ${update.data.entity.name} (${update.data.entity.type})`;
          break;
        case 'entity_updated':
          message = `Updated entity: ${update.data.entity.name}`;
          break;
        case 'entity_deleted':
          message = `Deleted entity: ${update.data.entity_id}`;
          break;
        case 'relationship_added':
          message = `Added relationship: ${update.data.relationship.type}`;
          break;
        case 'extraction_started':
          message = `Started extraction for scene ${update.data.scene_id}`;
          break;
        case 'extraction_progress':
          message = `Extraction progress: ${update.data.progress}%`;
          break;
        case 'extraction_completed':
          message = `Extraction completed: ${update.data.entities_found} entities, ${update.data.relationships_found} relationships`;
          break;
        case 'extraction_failed':
          message = `Extraction failed: ${update.data.error}`;
          break;
        default:
          message = `Update: ${update.type}`;
      }

      // Add to updates list
      const newUpdate: UpdateMessage = {
        id: `${Date.now()}-${Math.random()}`,
        type: update.type,
        message,
        timestamp: new Date(update.timestamp),
      };

      setUpdates(prev => [newUpdate, ...prev].slice(0, 50));  // Keep last 50 updates

      // Trigger refresh callback
      if (onUpdateReceived) {
        onUpdateReceived();
      }
    },
  });

  // Auto-dismiss updates after 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setUpdates(prev =>
        prev.filter(update => now - update.timestamp.getTime() < 10000)
      );
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!showNotifications && updates.length === 0) {
    return null;
  }

  return (
    <div className="live-graph-updates bg-gray-900 text-white p-4 rounded-lg">
      {/* Connection status */}
      <div className={`mb-3 flex items-center gap-2 text-sm ${connected ? 'text-green-400' : error ? 'text-red-400' : 'text-yellow-400'}`}>
        {connected ? (
          <>
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            Live updates active
          </>
        ) : error ? (
          <>
            <span className="w-2 h-2 bg-red-400 rounded-full"></span>
            Connection error: {error}
          </>
        ) : (
          <>
            <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
            Connecting...
          </>
        )}
      </div>

      {/* Toggle notifications */}
      <button
        onClick={() => setShowNotifications(!showNotifications)}
        className="mb-3 px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm transition-colors"
      >
        {showNotifications ? 'Hide' : 'Show'} Notifications
      </button>

      {/* Update feed */}
      {showNotifications && updates.length > 0 && (
        <div className="update-feed">
          <h3 className="text-lg font-semibold mb-3">Recent Updates</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {updates.map(update => (
              <div
                key={update.id}
                className={`p-3 rounded-lg ${
                  update.type.includes('failed') || update.type.includes('deleted')
                    ? 'bg-red-900 bg-opacity-30 border border-red-500'
                    : update.type.includes('completed') || update.type.includes('added')
                    ? 'bg-green-900 bg-opacity-30 border border-green-500'
                    : 'bg-blue-900 bg-opacity-30 border border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="text-sm flex-1">{update.message}</div>
                  <div className="text-xs text-gray-400 whitespace-nowrap">
                    {update.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveGraphUpdates;
