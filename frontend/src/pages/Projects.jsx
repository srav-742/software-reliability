import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { projectApi, analysisApi, predictApi } from '../services/api';
import {
  Folder,
  Plus,
  Search,
  Filter,
  Trash2,
  ExternalLink,
  BarChart3,
  BrainCircuit,
  FileCode2,
  GitBranch,
  CheckCircle2,
  AlertCircle,
  Clock,
} from 'lucide-react';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLang, setSelectedLang] = useState('All');
  const [actionLoading, setActionLoading] = useState({});

  const fetchProjects = async () => {
    try {
      const res = await projectApi.getAll();
      setProjects(res.data || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete project "${name}"?`)) return;
    try {
      await projectApi.delete(id);
      setProjects(projects.filter((p) => p.id !== id));
    } catch (err) {
      alert('Failed to delete project: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleAnalyze = async (id) => {
    setActionLoading((prev) => ({ ...prev, [id]: 'analyzing' }));
    try {
      await analysisApi.analyzeProject(id);
      alert('Analysis completed successfully!');
      fetchProjects();
    } catch (err) {
      alert('Analysis failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setActionLoading((prev) => ({ ...prev, [id]: null }));
    }
  };

  const filteredProjects = projects.filter((p) => {
    const matchesSearch =
      p.project_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLang = selectedLang === 'All' || p.language === selectedLang;
    return matchesSearch && matchesLang;
  });

  const languages = ['All', ...new Set(projects.map((p) => p.language).filter(Boolean))];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Software Projects</h1>
          <p className="text-slate-400 text-sm">Manage source code repositories registered for reliability evaluation</p>
        </div>

        <Link
          to="/projects/create"
          className="px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          Create New Project
        </Link>
      </div>

      {/* Controls Bar: Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search projects by name or description..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950/60 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            className="px-3 py-2 bg-slate-950/60 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                Language: {lang}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Project Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project) => (
          <div
            key={project.id}
            className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700/80 transition-all backdrop-blur-sm flex flex-col justify-between group"
          >
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-cyan-400 group-hover:scale-105 transition-transform">
                    <FileCode2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base leading-tight hover:text-cyan-400 transition-colors">
                      <Link to={`/projects/${project.id}`}>{project.project_name}</Link>
                    </h3>
                    <span className="text-[11px] text-slate-400 font-mono">ID: #{project.id}</span>
                  </div>
                </div>

                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-semibold tracking-wider uppercase border ${
                    project.status === 'completed'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : project.status === 'analyzed'
                      ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}
                >
                  {project.status || 'Registered'}
                </span>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-400 line-clamp-2">
                {project.description || 'No description provided.'}
              </p>

              {/* Metadata Badges */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/60">
                <span className="px-2 py-1 rounded bg-slate-800 text-[11px] font-medium text-slate-300">
                  {project.language}
                </span>
                {project.framework && (
                  <span className="px-2 py-1 rounded bg-slate-800 text-[11px] font-medium text-slate-400">
                    {project.framework}
                  </span>
                )}
                {project.repository_url && (
                  <a
                    href={project.repository_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-[11px] text-cyan-400 hover:underline ml-auto"
                  >
                    <GitBranch className="w-3 h-3" /> Repo
                  </a>
                )}
              </div>
            </div>

            {/* Actions Bar */}
            <div className="mt-6 pt-4 border-t border-slate-800/60 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleAnalyze(project.id)}
                  disabled={actionLoading[project.id]}
                  className="px-3 py-1.5 rounded-lg bg-cyan-950/60 border border-cyan-800/60 hover:bg-cyan-900/60 text-cyan-300 text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                  title="Run automated feature extraction"
                >
                  <BarChart3 className="w-3.5 h-3.5" />
                  {actionLoading[project.id] === 'analyzing' ? 'Analyzing...' : 'Analyze'}
                </button>

                <Link
                  to={`/prediction?project_id=${project.id}`}
                  className="px-3 py-1.5 rounded-lg bg-blue-950/60 border border-blue-800/60 hover:bg-blue-900/60 text-blue-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  title="Run reliability prediction"
                >
                  <BrainCircuit className="w-3.5 h-3.5" />
                  Predict
                </Link>
              </div>

              <div className="flex items-center gap-1">
                <Link
                  to={`/projects/${project.id}`}
                  className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                  title="View Details"
                >
                  <ExternalLink className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(project.id, project.project_name)}
                  className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                  title="Delete Project"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {filteredProjects.length === 0 && (
          <div className="col-span-full py-16 text-center bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl space-y-3">
            <Folder className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-semibold text-slate-300">No Projects Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Get started by creating a new project and uploading your source code ZIP file for analysis.
            </p>
            <Link
              to="/projects/create"
              className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-white font-semibold rounded-xl text-xs transition-all shadow-md shadow-cyan-500/20"
            >
              <Plus className="w-4 h-4" />
              Create Project
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
