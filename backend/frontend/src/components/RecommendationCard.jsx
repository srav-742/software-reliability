import React, { useState } from 'react';
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Code2,
  GitFork,
  Database,
  Layers,
  Cpu,
  HardDrive,
  FileCode,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Zap,
} from 'lucide-react';
import { parseRecommendation } from '../utils/recommendationFormatter';

const getCategoryIcon = (category = '') => {
  const cat = category.toLowerCase();
  if (cat.includes('nest')) return GitFork;
  if (cat.includes('query') || cat.includes('database')) return Database;
  if (cat.includes('complex')) return Code2;
  if (cat.includes('loc') || cat.includes('line')) return FileCode;
  if (cat.includes('dup')) return Layers;
  if (cat.includes('cpu')) return Cpu;
  if (cat.includes('memory')) return HardDrive;
  return Sparkles;
};

const getSeverityBadge = (severity = 'Medium') => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    case 'high':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    case 'medium':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
    default:
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  }
};

export default function RecommendationCard({ rawRecommendation, index = 0 }) {
  const item = parseRecommendation(rawRecommendation);
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [resolved, setResolved] = useState(false);

  if (!item) return null;

  const CategoryIcon = getCategoryIcon(item.category);
  const severityBadge = getSeverityBadge(item.severity);

  const handleCopySnippet = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(item.codeTip);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`group relative rounded-2xl border transition-all duration-300 overflow-hidden ${
        resolved
          ? 'bg-slate-900/40 border-slate-800/50 opacity-60'
          : 'bg-slate-900/80 border-slate-800 hover:border-cyan-500/40 hover:shadow-lg hover:shadow-cyan-500/5 backdrop-blur-md'
      }`}
    >
      {/* Top Banner Accent */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 opacity-60 group-hover:opacity-100 transition-opacity" />

      <div className="p-5 space-y-4">
        {/* Card Header: Category & Impact */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-cyan-400 group-hover:border-cyan-500/30 transition-colors">
              <CategoryIcon className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Category
              </span>
              <h4 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                {item.category}
              </h4>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold border ${severityBadge}`}
            >
              {item.severity} Risk
            </span>

            <span className="px-2.5 py-1 rounded-full text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1">
              <Zap className="w-3 h-3" />
              {item.impact}
            </span>
          </div>
        </div>

        {/* Actionable Guidance (Main Prompt Spec: "Refactor long methods", "Reduce nested conditions", "Optimize SQL queries") */}
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 flex items-start justify-between gap-3">
          <div className="space-y-1">
            <span className="text-[10px] font-semibold text-cyan-400 uppercase tracking-widest block">
              Action Required
            </span>
            <p className="text-sm font-semibold text-slate-100 leading-snug">
              {item.action}
            </p>
          </div>
        </div>

        {/* Action Buttons & Expand Toggle */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-xs">
          <button
            onClick={() => setResolved(!resolved)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all ${
              resolved
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{resolved ? 'Resolved' : 'Mark Addressed'}</span>
          </button>

          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 font-semibold transition-all text-[11px]"
          >
            <span>{expanded ? 'Hide Refactoring Tip' : 'View Code Fix Tip'}</span>
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Collapsible Refactoring Guidance Snippet */}
        {expanded && (
          <div className="pt-3 border-t border-slate-800 space-y-3 animate-in fade-in duration-200">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-slate-400">Refactoring Implementation Snippet</span>
                <button
                  onClick={handleCopySnippet}
                  className="flex items-center gap-1 px-2 py-1 text-[10px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition-colors"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <pre className="p-3 rounded-lg bg-slate-900 font-mono text-xs text-cyan-300 overflow-x-auto border border-slate-800/80 leading-relaxed">
                {item.codeTip}
              </pre>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed italic">
              {item.detail}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
