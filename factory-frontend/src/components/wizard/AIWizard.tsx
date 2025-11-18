/**
 * AI Wizard Chat Component
 *
 * Conversational interface to guide users through:
 * - Project creation and setup
 * - NotebookLM configuration
 * - Knowledge Graph initialization
 * - Scene writing with AI assistance
 *
 * Makes complex features accessible through natural conversation
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardMessage } from './WizardMessage';

interface Message {
  id: string;
  role: 'wizard' | 'user';
  content: string;
  timestamp: Date;
  actions?: WizardAction[];
}

interface WizardAction {
  type: 'button' | 'input' | 'link';
  label: string;
  value?: string;
  onClick?: () => void;
  href?: string;
}

interface AIWizardProps {
  projectId?: string;
  context?: 'onboarding' | 'project-setup' | 'notebooklm' | 'knowledge-graph' | 'copilot';
  onComplete?: () => void;
}

export const AIWizard: React.FC<AIWizardProps> = ({
  projectId,
  context = 'onboarding',
  onComplete
}) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [wizardState, setWizardState] = useState({
    step: 0,
    context,
    projectId,
    userData: {} as any
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize conversation based on context
  useEffect(() => {
    initializeConversation();
  }, [context]);

  const initializeConversation = () => {
    const welcomeMessages = getWelcomeMessages(context);
    welcomeMessages.forEach((msg, index) => {
      setTimeout(() => {
        addWizardMessage(msg.content, msg.actions);
      }, index * 1000);
    });
  };

  const getWelcomeMessages = (ctx: string) => {
    switch (ctx) {
      case 'onboarding':
        return [
          {
            content: "👋 Welcome to Writers Factory! I'm your AI writing assistant.",
            actions: []
          },
          {
            content: "I'll help you set up your first project and show you around. What kind of story are you working on?",
            actions: [
              { type: 'button' as const, label: 'Science Fiction', value: 'sci-fi' },
              { type: 'button' as const, label: 'Fantasy', value: 'fantasy' },
              { type: 'button' as const, label: 'Mystery', value: 'mystery' },
              { type: 'button' as const, label: 'Other', value: 'other' }
            ]
          }
        ];

      case 'notebooklm':
        return [
          {
            content: "📚 Let's set up NotebookLM integration for research-grounded writing!",
            actions: []
          },
          {
            content: "NotebookLM lets you ground your story in real research - YouTube videos, PDFs, articles, and more. Have you created any NotebookLM notebooks yet?",
            actions: [
              { type: 'button' as const, label: 'Yes, I have notebooks', value: 'has-notebooks' },
              { type: 'button' as const, label: 'No, show me how', value: 'need-help' }
            ]
          }
        ];

      case 'knowledge-graph':
        return [
          {
            content: "🕸️ Knowledge Graphs help you track characters, locations, and relationships in your story.",
            actions: []
          },
          {
            content: "Would you like me to extract entities from your existing scenes, or start fresh?",
            actions: [
              { type: 'button' as const, label: 'Extract from scenes', value: 'extract' },
              { type: 'button' as const, label: 'Start fresh', value: 'fresh' }
            ]
          }
        ];

      case 'copilot':
        return [
          {
            content: "🤖 The AI Copilot helps you write scenes with real-time suggestions!",
            actions: []
          },
          {
            content: "It can run locally (FREE with Ollama) or use premium models (Claude, GPT-4). Which would you prefer?",
            actions: [
              { type: 'button' as const, label: 'FREE Local AI (Ollama)', value: 'ollama' },
              { type: 'button' as const, label: 'Premium Models', value: 'premium' }
            ]
          }
        ];

      default:
        return [
          {
            content: "Hi! How can I help you today?",
            actions: [
              { type: 'button' as const, label: 'Create a project', value: 'create-project' },
              { type: 'button' as const, label: 'Set up NotebookLM', value: 'setup-notebooklm' },
              { type: 'button' as const, label: 'Learn about features', value: 'learn' }
            ]
          }
        ];
    }
  };

  const addWizardMessage = (content: string, actions?: WizardAction[]) => {
    setIsTyping(true);
    setTimeout(() => {
      const newMessage: Message = {
        id: `wizard-${Date.now()}`,
        role: 'wizard',
        content,
        timestamp: new Date(),
        actions
      };
      setMessages(prev => [...prev, newMessage]);
      setIsTyping(false);
    }, 500);
  };

  const addUserMessage = (content: string) => {
    const newMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleActionClick = (action: WizardAction) => {
    if (action.value) {
      addUserMessage(action.label);
      handleUserResponse(action.value);
    } else if (action.onClick) {
      action.onClick();
    } else if (action.href) {
      navigate(action.href);
    }
  };

  const handleUserResponse = (value: string) => {
    // Update wizard state based on response
    const newState = { ...wizardState };
    newState.step += 1;

    // Context-specific logic
    switch (wizardState.context) {
      case 'onboarding':
        handleOnboardingFlow(value, newState);
        break;
      case 'notebooklm':
        handleNotebookLMFlow(value, newState);
        break;
      case 'knowledge-graph':
        handleKnowledgeGraphFlow(value, newState);
        break;
      case 'copilot':
        handleCopilotFlow(value, newState);
        break;
    }

    setWizardState(newState);
  };

  const handleOnboardingFlow = (value: string, state: any) => {
    if (state.step === 1) {
      // Genre selected
      state.userData.genre = value;
      addWizardMessage(`Great! ${value} is an exciting genre. What's your project name?`);
    } else if (state.step === 2) {
      // Project name provided
      state.userData.projectName = value;
      addWizardMessage(
        `Perfect! I'll create "${value}" for you. Would you like to set up NotebookLM for research?`,
        [
          { type: 'button', label: 'Yes, set up research', value: 'setup-research' },
          { type: 'button', label: 'Skip for now', value: 'skip-research' }
        ]
      );
    } else if (state.step === 3) {
      if (value === 'setup-research') {
        addWizardMessage(
          'Excellent! Let me guide you through NotebookLM setup.',
          [
            {
              type: 'button',
              label: 'Continue to NotebookLM Setup',
              onClick: () => {
                setWizardState({ ...state, context: 'notebooklm', step: 0 });
                initializeConversation();
              }
            }
          ]
        );
      } else {
        addWizardMessage(
          "No problem! You can add research later. Let's create your project now.",
          [
            {
              type: 'button',
              label: 'Create Project',
              onClick: () => createProject(state.userData)
            }
          ]
        );
      }
    }
  };

  const handleNotebookLMFlow = (value: string, state: any) => {
    if (state.step === 1) {
      if (value === 'has-notebooks') {
        addWizardMessage(
          "Perfect! You can configure up to 3 notebooks: Character Research, World Building, and Themes. Ready to add them?",
          [
            {
              type: 'button',
              label: 'Configure Notebooks',
              href: projectId ? `/projects/${projectId}/notebooklm` : '/notebooklm'
            }
          ]
        );
      } else {
        addWizardMessage(
          "No worries! Here's how to create a NotebookLM notebook:\n\n1. Go to notebooklm.google.com\n2. Create a new notebook\n3. Add your research sources (YouTube videos, PDFs, etc.)\n4. Copy the notebook URL\n5. Come back and paste it here!",
          [
            {
              type: 'button',
              label: 'Open NotebookLM',
              href: 'https://notebooklm.google.com'
            },
            {
              type: 'button',
              label: 'I created one',
              value: 'has-notebooks'
            }
          ]
        );
      }
    }
  };

  const handleKnowledgeGraphFlow = (value: string, state: any) => {
    if (state.step === 1) {
      if (value === 'extract') {
        addWizardMessage(
          "Great! I'll extract entities from your scenes. This will create characters, locations, and relationships automatically.",
          [
            {
              type: 'button',
              label: 'Start Extraction',
              onClick: () => startEntityExtraction()
            }
          ]
        );
      } else {
        addWizardMessage(
          "Perfect! You can add entities manually as you write, or I can extract them later. Let's start writing!",
          [
            {
              type: 'button',
              label: 'Go to Editor',
              href: projectId ? `/projects/${projectId}/editor` : '/projects'
            }
          ]
        );
      }
    }
  };

  const handleCopilotFlow = (value: string, state: any) => {
    if (state.step === 1) {
      state.userData.copilotType = value;
      if (value === 'ollama') {
        addWizardMessage(
          "Excellent choice! Ollama runs AI models locally on your computer - completely FREE. To get started:\n\n1. Install Ollama from ollama.ai\n2. Run: ollama pull llama2\n3. The copilot will work automatically!",
          [
            {
              type: 'button',
              label: 'Open Ollama Website',
              href: 'https://ollama.ai'
            },
            {
              type: 'button',
              label: 'I installed Ollama',
              value: 'ollama-installed'
            }
          ]
        );
      } else {
        addWizardMessage(
          "Premium models offer the best quality. You'll need API keys for:\n\n• Claude (Anthropic)\n• GPT-4 (OpenAI)\n• Gemini (Google)\n\nWould you like to add your API keys now?",
          [
            {
              type: 'button',
              label: 'Add API Keys',
              href: '/settings/api-keys'
            },
            {
              type: 'button',
              label: 'Later',
              value: 'skip-api'
            }
          ]
        );
      }
    }
  };

  const createProject = async (userData: any) => {
    addWizardMessage('Creating your project...');

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          title: userData.projectName,
          genre: userData.genre
        })
      });

      if (response.ok) {
        const project = await response.json();
        addWizardMessage(
          `🎉 Success! "${userData.projectName}" is ready. Let's start writing!`,
          [
            {
              type: 'button',
              label: 'Go to Editor',
              href: `/projects/${project.id}/editor`
            }
          ]
        );
        onComplete?.();
      } else {
        addWizardMessage('Sorry, there was an error creating your project. Please try again.');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      addWizardMessage('Sorry, there was an error creating your project. Please try again.');
    }
  };

  const startEntityExtraction = async () => {
    addWizardMessage('Starting entity extraction...');

    try {
      const response = await fetch(`/api/knowledge-graph/projects/${projectId}/extract`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        addWizardMessage(
          '✅ Extraction started! I\'ll notify you when it\'s done.',
          [
            {
              type: 'button',
              label: 'View Knowledge Graph',
              href: `/projects/${projectId}/knowledge-graph`
            }
          ]
        );
        onComplete?.();
      } else {
        addWizardMessage('Sorry, there was an error starting extraction. Please try again.');
      }
    } catch (error) {
      console.error('Error starting extraction:', error);
      addWizardMessage('Sorry, there was an error starting extraction. Please try again.');
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    addUserMessage(inputValue);
    handleUserResponse(inputValue);
    setInputValue('');
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 rounded-lg border border-gray-700">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700 bg-gradient-to-r from-blue-900/30 to-purple-900/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            🧙‍♂️
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">AI Writing Wizard</h2>
            <p className="text-xs text-gray-400">Your guide to Writers Factory</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <WizardMessage
            key={message.id}
            message={message}
            onActionClick={handleActionClick}
          />
        ))}

        {isTyping && (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-sm">
              🧙‍♂️
            </div>
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIWizard;
