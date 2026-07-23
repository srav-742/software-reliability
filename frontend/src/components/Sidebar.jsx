import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Folder,
  FolderPlus,
  BarChart3,
  BrainCircuit,
  Eye,
  Sparkles,
  Cpu,
  FileSpreadsheet,
  User,
  Settings,
  ShieldCheck,
  FileCode2,
  GitPullRequest,
  KeyRound,
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/projects', label: 'Projects', icon: Folder },
  { path: '/projects/create', label: 'Create Project', icon: FolderPlus },
  { path: '/analysis', label: 'Code Analysis', icon: BarChart3 },
  { path: '/prediction', label: 'Reliability Prediction', icon: BrainCircuit },
  { path: '/explainability', label: 'SHAP Explainability', icon: Eye },
  { path: '/recommendations', label: 'AI Recommendations', icon: Sparkles },
  { path: '/training', label: 'Model Training', icon: Cpu },
  { path: '/cicd', label: 'CI/CD Integration', icon: GitPullRequest },
  { path: '/api-key-scanner', label: 'API Key Scanner', icon: KeyRound },
  { path: '/reports', label: 'Reports', icon: FileSpreadsheet },
  { path: '/profile', label: 'Profile', icon: User },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ isOpen, setIsOpen }) {
  return (
    <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 flex flex-col`}>
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight">ReliabilityAI</h1>
            <p className="text-[10px] text-cyan-400 font-mono tracking-wider uppercase">Software Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <div className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Platform Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer System Badge */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-slate-300 font-medium">FastAPI Engine</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}
