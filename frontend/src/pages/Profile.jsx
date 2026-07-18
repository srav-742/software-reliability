import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User, Mail, ShieldCheck, Briefcase, Calendar, Key, Lock } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Engineer Profile</h1>
        <p className="text-slate-400 text-sm">Account details, role permissions, and active platform tokens</p>
      </div>

      {/* Main Profile Card */}
      <div className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b border-slate-800">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white text-3xl shadow-xl shadow-cyan-500/20">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>

          <div className="text-center sm:text-left space-y-1">
            <h2 className="text-xl font-bold text-white">{user?.full_name || 'Engineer Name'}</h2>
            <p className="text-xs text-slate-400 font-mono">{user?.email}</p>
            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-1">
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-semibold capitalize">
                {user?.role || 'Developer'}
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                Active Session
              </span>
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-slate-900 text-slate-400">
              <User className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] text-slate-500 block">Full Name</span>
              <span className="font-semibold text-slate-200 text-sm">{user?.full_name || 'N/A'}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-slate-900 text-slate-400">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] text-slate-500 block">Email Address</span>
              <span className="font-semibold text-slate-200 text-sm">{user?.email || 'N/A'}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-slate-900 text-slate-400">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] text-slate-500 block">Role / Designation</span>
              <span className="font-semibold text-slate-200 text-sm capitalize">{user?.role || 'Developer'}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-slate-900 text-slate-400">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <span className="text-[11px] text-slate-500 block">Authentication Method</span>
              <span className="font-semibold text-slate-200 text-sm">JWT Bearer + Firebase Sync</span>
            </div>
          </div>
        </div>

        {/* Security Token status */}
        <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Key className="w-4 h-4 text-cyan-400" /> JWT Session Token
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">Valid</span>
          </div>
          <p className="text-[11px] text-slate-500 font-mono truncate">
            {localStorage.getItem('token') ? `${localStorage.getItem('token').slice(0, 40)}...` : 'No token'}
          </p>
        </div>
      </div>
    </div>
  );
}
