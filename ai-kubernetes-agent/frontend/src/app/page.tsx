'use client';

import { useState, useEffect } from 'react';
import { Play, MessageSquare, CheckCircle2, Loader2, Circle, AlertCircle } from 'lucide-react';

const PROGRESS_STEPS = [
  'Checking Pods',
  'Reading Logs',
  'Analyzing Events',
  'Inspecting Deployments',
  'Checking Networking',
  'AI Reasoning Engine',
  'Root Cause Found',
];

export default function Dashboard() {
  const [history, setHistory] = useState<any[]>([]);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [diagnosis, setDiagnosis] = useState<any | null>(null);
  const [targetNamespace, setTargetNamespace] = useState('default');

  useEffect(() => {
    fetch('http://127.0.0.1:8000/history')
      .then((res) => res.json())
      .then((data) => setHistory(data.history || []))
      .catch((err) => console.error('Failed to fetch history', err));
  }, []);

  const handleInvestigate = async () => {
    setIsInvestigating(true);
    setDiagnosis(null);
    setCurrentStep(0);

    const progressInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < PROGRESS_STEPS.length - 2 ? prev + 1 : prev));
    }, 1500);

    try {
      const response = await fetch('http://127.0.0.1:8000/investigate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ namespace: targetNamespace })
      });
      const data = await response.json();
      
      
      clearInterval(progressInterval);
      setCurrentStep(PROGRESS_STEPS.length);
      setDiagnosis(data.diagnosis);
      
      setHistory((prev) => [{
        timestamp: new Date().toLocaleString(),
        root_cause: data.diagnosis.root_cause,
        namespace: targetNamespace,
        confidence: data.diagnosis.confidence,
        status: 'success'
      }, ...prev]);

    } catch (error) {
      clearInterval(progressInterval);
      setCurrentStep(-1);
      alert('Investigation failed. Check backend connection.');
    } finally {
      setIsInvestigating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* HEADER & ACTIONS */}
        <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">AI Kubernetes Agent</h1>
            <p className="text-gray-500 text-sm mt-1">Automated Cluster SRE & Diagnostics</p>
          </div>
          <div className="flex gap-4">
            {/* NEW NAMESPACE SELECTOR */}
            <div className="flex items-center bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
              <span className="px-3 text-sm font-medium text-gray-500 bg-gray-100 border-r border-gray-200">
                Namespace
              </span>
              <input 
                type="text" 
                value={targetNamespace}
                onChange={(e) => setTargetNamespace(e.target.value)}
                placeholder="default"
                className="px-3 py-2 text-sm bg-transparent outline-none w-32 font-mono text-gray-700 focus:bg-white transition-colors"
                disabled={isInvestigating}
              />
            </div>
            <button className="flex items-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors font-medium">
              <MessageSquare size={18} />
              Chat Bot
            </button>
            <button 
              onClick={handleInvestigate}
              disabled={isInvestigating}
              className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isInvestigating ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
              {isInvestigating ? 'Investigating...' : 'Investigate Cluster'}
            </button>
          </div>
        </div>

        {/* PROGRESS & DIAGNOSIS GRID */}
        {(currentStep >= 0 || diagnosis) && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-fit">
              <h2 className="font-semibold mb-4">Investigation Progress</h2>
              <div className="space-y-4">
                {PROGRESS_STEPS.map((step, index) => {
                  let status = 'pending';
                  if (currentStep > index) status = 'done';
                  if (currentStep === index) status = 'active';

                  return (
                    <div key={step} className="flex items-center gap-3">
                      {status === 'done' && <CheckCircle2 size={20} className="text-green-500" />}
                      {status === 'active' && <Loader2 size={20} className="text-blue-500 animate-spin" />}
                      {status === 'pending' && <Circle size={20} className="text-gray-300" />}
                      <span className={`text-sm ${status === 'active' ? 'text-blue-700 font-medium' : status === 'done' ? 'text-gray-700' : 'text-gray-400'}`}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {diagnosis && (
              <div className="md:col-span-2 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-2 text-red-600 bg-red-50 px-3 py-1 rounded-full text-sm font-semibold">
                      <AlertCircle size={16} />
                      Root Cause Identified
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">{diagnosis.confidence}%</div>
                      <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">AI Confidence</div>
                    </div>
                  </div>
                  
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{diagnosis.root_cause}</h3>
                  <p className="text-gray-600 text-sm mb-6">{diagnosis.explanation}</p>

                  <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-100">
                    <h4 className="text-sm font-semibold text-gray-900 mb-1">Suggested Fix:</h4>
                    <p className="text-sm text-gray-700">{diagnosis.fix}</p>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">Execute Command:</h4>
                    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono shadow-inner">
                      <code>{diagnosis.kubectl_command}</code>
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* HISTORY TABLE */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Recent Investigations</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-6 py-3 font-medium">Timestamp</th>
                  <th className="px-6 py-3 font-medium">Root Cause</th>
                  <th className="px-6 py-3 font-medium">Namespace</th>
                  <th className="px-6 py-3 font-medium">Confidence</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.map((run, i) => (
                  <tr key={i} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-gray-500 whitespace-nowrap">{run.timestamp}</td>
                    <td className="px-6 py-4 font-medium text-gray-900 truncate max-w-xs">{run.root_cause}</td>
                    <td className="px-6 py-4 text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded-md text-xs">{run.namespace}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`font-medium ${run.confidence > 90 ? 'text-green-600' : 'text-yellow-600'}`}>
                        {run.confidence}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 py-1 px-2 rounded-md text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                        <CheckCircle2 size={12} />
                        Success
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}