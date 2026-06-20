'use client';

import { useState, useEffect } from 'react';
import { checkHealth } from '@/services/api';

export default function Home() {
  const [systemStatus, setSystemStatus] = useState<string>('Checking...');
  const [isInvestigating, setIsInvestigating] = useState(false);

  useEffect(() => {
    // Check backend connection on load
    const verifySystem = async () => {
      try {
        const data = await checkHealth();
        if (data.status === 'healthy') {
          setSystemStatus('Ready');
        }
      } catch (error) {
        setSystemStatus('Offline (Backend unreachable)');
      }
    };
    verifySystem();
  }, []);

  const handleInvestigate = () => {
    setIsInvestigating(true);
    // Placeholder logic for Phase 2 implementation
    setTimeout(() => {
      setIsInvestigating(false);
    }, 2000);
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8 space-y-8 text-center border border-gray-100">
        
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">
            AI Kubernetes Agent
          </h1>
          <p className="text-lg text-gray-500">
            Troubleshoot Kubernetes with AI
          </p>
        </div>

        <div className="pt-8 pb-4">
          <button
            onClick={handleInvestigate}
            disabled={systemStatus !== 'Ready' || isInvestigating}
            className={`px-8 py-4 rounded-lg font-semibold text-white transition-all shadow-md 
              ${systemStatus !== 'Ready' 
                ? 'bg-gray-400 cursor-not-allowed' 
                : isInvestigating 
                  ? 'bg-blue-400 animate-pulse' 
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg active:scale-95'}`}
          >
            {isInvestigating ? 'Investigating...' : '[ Investigate Cluster ]'}
          </button>
        </div>

        <div className="pt-8 border-t border-gray-100 flex items-center justify-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${systemStatus === 'Ready' ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm font-medium text-gray-600">
            System Status: {systemStatus}
          </span>
        </div>

      </div>
    </main>
  );
}