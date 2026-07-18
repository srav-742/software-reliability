import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { projectApi, analysisApi, predictApi } from '../services/api';
import {
  Folder,
  BarChart3,
  BrainCircuit,
  Eye,
  ArrowLeft,
  FileCode2,
  GitBranch,
  Calendar,
  Layers,
  Code2,
  Activity,
  Trash2,
  Zap,
} from 'lucide-react';

export default function ProjectDetails() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const [projRes, metricRes, predRes] = await Promise.allSettled([
          projectApi.getById(id),
          analysisApi.getMetrics(id),
          predictApi.getHistoryByProject(id),
        ]);

        if (projRes.status === 'fulfilled') setProject(projRes.value.data);
        if (metricRes.status === 'fulfilled') setMetrics(metricRes.value.data);
        if (predRes.status === 'fulfilled') setPredictions(predRes.value.data || []);
      } catch (err) {
        console.error('Failed to load project details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]);

  const handleRunAnalysis = async () => {
    setActionLoading(true);
    try {
      const res = await analysisApi.analyzeProject(id);
      setMetrics(res.data);
      alert('Code analysis completed!');
    } catch (err) {
      alert('Analysis failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this project permanently?')) return;
    try {
      await projectApi.delete(id);
      navigate('/projects');
    } catch (err) {
      alert('Delete failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-16">
        <h2 className="text-xl font-bold text-slate-300">Project Not Found</h2>
        <Link to="/projects" className="text-xs text-cyan-400 hover:underline mt-2 inline-block">
          Return to Projects
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header & Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link
            to="/projects"
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">{project.project_name}</h1>
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-semibold">
                {project.language}
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-1">{project.description || 'No description provided.'}</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunAnalysis}
            disabled={actionLoading}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 flex items-center gap-2 transition-all disabled:opacity-50"
          >
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            {actionLoading ? 'Analyzing...' : 'Run Code Analysis'}
          </button>

          <Link
            to={`/prediction?project_id=${project.id}`}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all"
          >
            <BrainCircuit className="w-4 h-4" />
            Run ML Prediction
          </Link>

          <button
            onClick={handleDelete}
            className="p-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-400 transition-colors"
            title="Delete Project"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Project Metadata Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <span className="text-xs text-slate-500 block mb-1">Framework</span>
          <span className="font-semibold text-slate-200 text-sm">{project.framework || 'Standard'}</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <span className="text-xs text-slate-500 block mb-1">Source Code Path</span>
          <span className="font-mono text-xs text-slate-300 truncate block">
            {project.source_code_path || 'None uploaded'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <span className="text-xs text-slate-500 block mb-1">Repository</span>
          {project.repository_url ? (
            <a
              href={project.repository_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-cyan-400 hover:underline truncate block"
            >
              {project.repository_url}
            </a>
          ) : (
            <span className="text-xs text-slate-500">Not linked</span>
          )}
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <span className="text-xs text-slate-500 block mb-1">Created At</span>
          <span className="font-mono text-xs text-slate-300">
            {new Date(project.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Code Metrics Snapshot */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Extracted Metrics Overview</h3>
            <p className="text-xs text-slate-400">Static AST and complexity parameters extracted from code</p>
          </div>
          {metrics && (
            <Link
              to={`/analysis?project_id=${project.id}`}
              className="text-xs text-cyan-400 hover:underline font-semibold"
            >
              Full Analysis Details &rarr;
            </Link>
          )}
        </div>

        {metrics ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">Lines of Code (LOC)</span>
              <span className="text-xl font-extrabold text-cyan-400">{metrics.lines_of_code || 0}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">Cyclomatic Complexity</span>
              <span className="text-xl font-extrabold text-amber-400">
                {(metrics.cyclomatic_complexity || 0).toFixed(1)}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">Maintainability Index</span>
              <span className="text-xl font-extrabold text-emerald-400">
                {(metrics.maintainability_index || 0).toFixed(1)}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">Halstead Volume</span>
              <span className="text-xl font-extrabold text-slate-200">
                {(metrics.halstead_volume || 0).toFixed(0)}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">AST Max Depth</span>
              <span className="text-xl font-extrabold text-slate-200">{metrics.ast_depth || 0}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-1">Dependencies</span>
              <span className="text-xl font-extrabold text-slate-200">{metrics.dependencies_count || 0}</span>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center bg-slate-950/40 border border-dashed border-slate-800 rounded-xl space-y-2">
            <Activity className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400 font-medium">No extracted metrics available yet.</p>
            <button
              onClick={handleRunAnalysis}
              className="text-xs text-cyan-400 hover:underline font-semibold"
            >
              Run Code Analysis Now
            </button>
          </div>
        )}
      </div>

      {/* Predictions History for Project */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Project Prediction Runs</h3>
            <p className="text-xs text-slate-400">Historical reliability predictions for this codebase</p>
          </div>
          <Link
            to={`/explainability?project_id=${project.id}`}
            className="text-xs text-cyan-400 hover:underline font-semibold flex items-center gap-1"
          >
            <Eye className="w-3.5 h-3.5" /> SHAP Feature Explanation
          </Link>
        </div>

        <div className="space-y-3">
          {predictions.map((pred) => (
            <div
              key={pred.id}
              className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
                  <Zap className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-200 text-sm">
                      Failure Prob: {((pred.failure_probability || 0) * 100).toFixed(1)}%
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-slate-800 text-slate-300">
                      {pred.risk_level}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">
                    Model: {pred.model_used || 'CatBoost'} • Evaluated on{' '}
                    {new Date(pred.created_at).toLocaleString()}
                  </span>
                </div>
              </div>

              <Link
                to={`/prediction?project_id=${project.id}`}
                className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 text-xs font-semibold"
              >
                View Full Prediction
              </Link>
            </div>
          ))}

          {predictions.length === 0 && (
            <p className="text-center py-6 text-xs text-slate-500 italic">
              No predictions recorded for this project yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
