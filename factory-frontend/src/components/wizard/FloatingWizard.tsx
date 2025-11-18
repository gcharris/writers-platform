/**
 * Floating Wizard Button
 *
 * A floating action button that opens the AI Wizard in a modal
 * Can be added to any page for contextual help
 */

import React, { useState } from 'react';
import { AIWizard } from './AIWizard';

interface FloatingWizardProps {
  projectId?: string;
  context?: 'onboarding' | 'project-setup' | 'notebooklm' | 'knowledge-graph' | 'copilot';
  position?: 'bottom-right' | 'bottom-left';
}

export const FloatingWizard: React.FC<FloatingWizardProps> = ({
  projectId,
  context,
  position = 'bottom-right'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnread, setHasUnread] = useState(true); // Show pulse for first-time users

  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6'
  };

  const handleOpen = () => {
    setIsOpen(true);
    setHasUnread(false);
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={handleOpen}
          className={`fixed ${positionClasses[position]} z-40 group`}
          aria-label="Open AI Wizard"
        >
          <div className="relative">
            {/* Pulse Animation for unread */}
            {hasUnread && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
              </span>
            )}

            {/* Button */}
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg flex items-center justify-center text-2xl transform transition-all group-hover:scale-110 group-hover:shadow-xl">
              🧙‍♂️
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Need help? Ask the AI Wizard
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        </button>
      )}

      {/* Modal Wizard */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="w-full max-w-4xl h-[600px] relative">
            {/* Close Button */}
            <button
              onClick={() => setIsOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 text-sm flex items-center gap-2"
            >
              <span>Close</span>
              <span className="text-2xl">×</span>
            </button>

            {/* Wizard */}
            <AIWizard
              projectId={projectId}
              context={context}
              onComplete={() => setIsOpen(false)}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingWizard;
