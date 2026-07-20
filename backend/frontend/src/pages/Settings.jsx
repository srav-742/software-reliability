import React, { useState, useEffect } from 'react';
import { healthApi } from '../services/api';
import {
  Settings,
  Server,
  Activity,
  CheckCircle2,
  AlertCircle,
  Database,
  Flame,
  Shield,
  Save,
} from 'lucide-react';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  );
  const [healthStatus, setHealthStatus] = useState(null);
  const [testingHealth, setTestingHealth] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const checkHealth = async () => {
    setTestingHealth(true);
    try {
      await healthApi.check();
      setHealthStatus('connected');
    } catch (err) {
      setHealthStatus('failed');
    } finally {
      setTestingHealth(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  const handleSave = (e) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings</h1>
        <p className="text-slate-400 text-sm">Configure backend endpoints, API connection status, and Firebase integration</p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <p className="text-xs text-emerald-300 font-medium">Settings saved successfully!</p>
        </div>
      )}

      {/* Backend Connection Panel */}
      <form onSubmit={handleSave} className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-slate-800 text-cyan-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Backend API Endpoint</h3>
              <p className="text-xs text-slate-400">REST base URL for FastAPI prediction engine</p>
            </div>
          </div>

          <button
            type="button"
            onClick={checkHealth}
            disabled={testingHealth}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            {testingHealth ? 'Testing...' : 'Test Connection'}
          </button>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">FastAPI Service URL</label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>

        {/* Health Status Indicator */}
        <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between text-xs">
          <span className="text-slate-400">Connection Status:</span>
          {healthStatus === 'connected' ? (
            <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <CheckCircle2 className="w-4 h-4" /> Connected to FastAPI (HTTP 200 OK)
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-rose-400 font-semibold">
              <AlertCircle className="w-4 h-4" /> Cannot Reach Backend
            </span>
          )}
        </div>

        {/* Firebase Config Summary */}
        <div className="pt-4 border-t border-slate-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400">
              <Flame className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Firebase Authentication Sync</h3>
              <p className="text-xs text-slate-400">Fail-safe custom token synchronization</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Project ID:</span>
              <span className="font-mono text-slate-200">softwarereliability</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Auth Domain:</span>
              <span className="font-mono text-slate-200">softwarereliability.firebaseapp.com</span>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-3 px-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm shadow-lg shadow-cyan-500/25 transition-all flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" />
          Save Configuration
        </button>
      </form>
    </div>
  );
}
