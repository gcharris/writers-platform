/**
 * Wizard Message Component
 *
 * Displays individual chat messages from the wizard or user
 * with optional action buttons
 */

import React from 'react';

interface WizardAction {
  type: 'button' | 'input' | 'link';
  label: string;
  value?: string;
  onClick?: () => void;
  href?: string;
}

interface Message {
  id: string;
  role: 'wizard' | 'user';
  content: string;
  timestamp: Date;
  actions?: WizardAction[];
}

interface WizardMessageProps {
  message: Message;
  onActionClick: (action: WizardAction) => void;
}

export const WizardMessage: React.FC<WizardMessageProps> = ({ message, onActionClick }) => {
  const isWizard = message.role === 'wizard';

  return (
    <div className={`flex ${isWizard ? 'justify-start' : 'justify-end'} animate-fade-in`}>
      <div className={`flex gap-2 max-w-[80%] ${!isWizard && 'flex-row-reverse'}`}>
        {/* Avatar */}
        {isWizard && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-sm flex-shrink-0">
            🧙‍♂️
          </div>
        )}

        {/* Message Content */}
        <div>
          <div
            className={`rounded-lg px-4 py-3 ${
              isWizard
                ? 'bg-gray-800 text-white border border-gray-700'
                : 'bg-blue-600 text-white'
            }`}
          >
            {/* Text with line breaks preserved */}
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>

          {/* Actions */}
          {message.actions && message.actions.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.actions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => onActionClick(action)}
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm rounded-lg transition-all transform hover:scale-105 shadow-lg"
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}

          {/* Timestamp */}
          <p className={`text-xs text-gray-500 mt-1 ${!isWizard && 'text-right'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>

        {/* User Avatar */}
        {!isWizard && (
          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-sm flex-shrink-0">
            👤
          </div>
        )}
      </div>
    </div>
  );
};

export default WizardMessage;
