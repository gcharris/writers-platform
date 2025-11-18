/**
 * AI Copilot Editor
 * Real-time writing assistance with inline suggestions
 * Similar to Cursor AI or GitHub Copilot, but for creative writing
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';

interface CopilotEditorProps {
  projectId: string;
  sceneId?: string;
  initialContent: string;
  onContentChange: (content: string) => void;
  onSave?: () => void;
  placeholder?: string;
  className?: string;
  copilotEnabled?: boolean;
}

interface Suggestion {
  text: string;
  confidence: number;
  timestamp: string;
}

export const CopilotEditor: React.FC<CopilotEditorProps> = ({
  projectId,
  sceneId,
  initialContent,
  onContentChange,
  onSave,
  placeholder = "Start writing...",
  className = "",
  copilotEnabled = true,
}) => {
  // Editor state
  const [content, setContent] = useState(initialContent);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);
  const [showSuggestion, setShowSuggestion] = useState(false);
  const [copilotStatus, setCopilotStatus] = useState<'disconnected' | 'connected' | 'suggesting'>('disconnected');

  // Refs
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const suggestionRequestTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Get cursor position
  const getCursorPosition = useCallback(() => {
    if (textareaRef.current) {
      return textareaRef.current.selectionStart;
    }
    return 0;
  }, []);

  // Connect to copilot WebSocket
  useEffect(() => {
    if (!copilotEnabled || !projectId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsUrl = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');

    const ws = new WebSocket(`${wsUrl}/copilot/${projectId}/stream`);

    ws.onopen = () => {
      console.log('✅ Copilot connected');
      setCopilotStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'suggestion' && data.text) {
          setSuggestion({
            text: data.text,
            confidence: data.confidence || 0.85,
            timestamp: data.timestamp,
          });
          setShowSuggestion(true);
          setCopilotStatus('connected');
        } else if (data.type === 'no_suggestion') {
          setSuggestion(null);
          setShowSuggestion(false);
          setCopilotStatus('connected');
        } else if (data.type === 'error') {
          console.error('Copilot error:', data.message);
          setCopilotStatus('connected');
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setCopilotStatus('disconnected');
    };

    ws.onclose = () => {
      console.log('Copilot disconnected');
      setCopilotStatus('disconnected');
    };

    wsRef.current = ws;

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [projectId, copilotEnabled]);

  // Request suggestion (debounced)
  const requestSuggestion = useCallback((text: string, cursorPos: number) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    // Clear existing timer
    if (suggestionRequestTimerRef.current) {
      clearTimeout(suggestionRequestTimerRef.current);
    }

    // Request after short pause (user stopped typing)
    suggestionRequestTimerRef.current = setTimeout(() => {
      setCopilotStatus('suggesting');

      wsRef.current?.send(JSON.stringify({
        text: text,
        cursor: cursorPos,
        scene_id: sceneId,
        event: 'pause',  // User paused typing
      }));
    }, 800);  // Wait 800ms after user stops typing
  }, [sceneId]);

  // Handle text change
  const handleTextChange = (newText: string) => {
    setContent(newText);
    setSuggestion(null);  // Clear suggestion when user types
    setShowSuggestion(false);

    // Notify parent
    if (onContentChange) {
      onContentChange(newText);
    }

    // Request suggestion after pause
    if (copilotEnabled && newText.length > 10) {
      const cursorPos = textareaRef.current?.selectionStart || newText.length;
      requestSuggestion(newText, cursorPos);
    }
  };

  // Accept suggestion (Tab key)
  const acceptSuggestion = useCallback(() => {
    if (!suggestion || !showSuggestion) return;

    const cursorPos = getCursorPosition();
    const newContent =
      content.slice(0, cursorPos) +
      ' ' + suggestion.text +
      content.slice(cursorPos);

    setContent(newContent);
    setShowSuggestion(false);
    setSuggestion(null);

    // Notify parent
    if (onContentChange) {
      onContentChange(newContent);
    }

    // Move cursor to end of suggestion
    setTimeout(() => {
      if (textareaRef.current) {
        const newPos = cursorPos + suggestion.text.length + 1;
        textareaRef.current.selectionStart = newPos;
        textareaRef.current.selectionEnd = newPos;
        textareaRef.current.focus();
      }
    }, 0);
  }, [suggestion, showSuggestion, content, getCursorPosition, onContentChange]);

  // Dismiss suggestion (Esc key)
  const dismissSuggestion = useCallback(() => {
    setShowSuggestion(false);
    setSuggestion(null);
  }, []);

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Tab: Accept suggestion
    if (e.key === 'Tab' && showSuggestion && suggestion) {
      e.preventDefault();
      acceptSuggestion();
      return;
    }

    // Esc: Dismiss suggestion
    if (e.key === 'Escape' && showSuggestion) {
      e.preventDefault();
      dismissSuggestion();
      return;
    }

    // Ctrl/Cmd + S: Save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      if (onSave) {
        onSave();
      }
      return;
    }

    // Any other key: dismiss suggestion
    if (showSuggestion && !['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      dismissSuggestion();
    }
  };

  return (
    <div className={`copilot-editor-container relative ${className}`}>
      {/* Status indicator */}
      {copilotEnabled && (
        <div className="absolute top-2 right-2 z-10 flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full text-xs">
          <div className={`w-2 h-2 rounded-full ${
            copilotStatus === 'connected' ? 'bg-green-400' :
            copilotStatus === 'suggesting' ? 'bg-yellow-400 animate-pulse' :
            'bg-gray-400'
          }`}></div>
          <span className="text-gray-300">
            {copilotStatus === 'connected' ? 'Copilot ready' :
             copilotStatus === 'suggesting' ? 'Thinking...' :
             'Copilot offline'}
          </span>
          {copilotStatus === 'connected' && (
            <span className="text-green-400 font-semibold">FREE</span>
          )}
        </div>
      )}

      {/* Main editor */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => handleTextChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full h-96 p-6 bg-gray-900 text-white font-mono text-base leading-relaxed resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
          style={{ caretColor: 'white' }}
        />

        {/* Ghost text suggestion overlay */}
        {showSuggestion && suggestion && (
          <div className="absolute inset-0 pointer-events-none p-6 font-mono text-base leading-relaxed">
            {/* Invisible text to match cursor position */}
            <span className="invisible whitespace-pre-wrap">{content.slice(0, getCursorPosition())}</span>
            {/* Visible suggestion as ghost text */}
            <span className="text-gray-500 italic">
              {suggestion.text}
            </span>
          </div>
        )}
      </div>

      {/* Keyboard hint */}
      {showSuggestion && suggestion && (
        <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center gap-4">
            <span>
              <kbd className="px-2 py-1 bg-gray-800 rounded">Tab</kbd> to accept
            </span>
            <span>
              <kbd className="px-2 py-1 bg-gray-800 rounded">Esc</kbd> to dismiss
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-400">●</span>
            <span>{Math.round(suggestion.confidence * 100)}% confident</span>
          </div>
        </div>
      )}

      {/* Word count */}
      <div className="mt-2 text-sm text-gray-400">
        {content.split(/\s+/).filter(w => w.length > 0).length} words
        {copilotEnabled && copilotStatus === 'disconnected' && (
          <span className="ml-4 text-yellow-400">
            ⚠️ Start Ollama for AI suggestions
          </span>
        )}
      </div>
    </div>
  );
};

export default CopilotEditor;
