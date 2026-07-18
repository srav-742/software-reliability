import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { modelApi, healthApi } from '../services/api';
import { LogOut, User, Activity, Cpu, Menu, Shield } from 'lucide-react';

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const [activeModel, setActiveModel] = useState(null);
  const [systemHealthy, setSystemHealthy] = useState(true);

  useEffect(() => {
    const fetchSystemState = async () => {
      try {
        const modelRes = await modelApi.getActiveModel();
        setActiveModel(modelRes.data);
      } catch (err) {
        console.warn('Active model not set or unavailable:', err);
      }

      try {
        await healthApi.check();
        setSystemHealthy(true);
      } catch (err) {
        setSystemHealthy(false);
      }
    };

    fetchSystemState();
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Active Model Indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Active Model:</span>
          <span className="font-semibold text-slate-200">
            {activeModel ? activeModel.algorithm : 'Default CatBoost'}
          </span>
          {activeModel?.test_f1 && (
            <span className="ml-1 px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 font-mono text-[10px] border border-cyan-800/50">
              F1: {(activeModel.test_f1 * 100).toFixed(1)}%
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Health status indicator */}
        <div className="hidden lg:flex items-center gap-2 text-xs">
          <Activity className={`w-3.5 h-3.5 ${systemHealthy ? 'text-emerald-400' : 'text-rose-400'}`} />
          <span className="text-slate-400">Backend API:</span>
          <span className={`font-medium ${systemHealthy ? 'text-emerald-400' : 'text-rose-400'}`}>
            {systemHealthy ? 'Connected' : 'Offline'}
          </span>
        </div>

        {/* User Profile & Actions */}
        {user && (
          <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white text-sm shadow-md">
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="hidden md:block text-left">
                <p className="text-xs font-semibold text-slate-200 leading-tight">{user.full_name || 'Engineer'}</p>
                <p className="text-[10px] text-slate-400 capitalize">{user.role || 'Developer'}</p>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
