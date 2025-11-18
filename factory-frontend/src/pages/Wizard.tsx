/**
 * Wizard Page
 *
 * Full-page AI Wizard interface for guiding users through setup
 */

import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AIWizard } from '../components/wizard';

export const WizardPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const context = (searchParams.get('context') as any) || 'onboarding';
  const projectId = searchParams.get('projectId') || undefined;

  const handleComplete = () => {
    // Redirect based on context
    if (projectId) {
      navigate(`/projects/${projectId}`);
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Top Bar */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">Writers Factory Setup</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-400 hover:text-white transition-colors"
          >
            Skip Setup →
          </button>
        </div>
      </div>

      {/* Wizard Container */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-4xl h-[700px]">
          <AIWizard
            context={context}
            projectId={projectId}
            onComplete={handleComplete}
          />
        </div>
      </div>

      {/* Bottom Help Text */}
      <div className="px-6 py-4 border-t border-gray-800 bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <p className="text-sm text-gray-500 text-center">
            Need help? Check out our <a href="/docs" className="text-blue-400 hover:text-blue-300 underline">documentation</a> or <a href="/support" className="text-blue-400 hover:text-blue-300 underline">contact support</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default WizardPage;
