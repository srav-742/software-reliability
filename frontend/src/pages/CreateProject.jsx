import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { projectApi } from '../services/api';
import {
  FolderPlus,
  Upload,
  FileCode2,
  GitBranch,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Code2,
  Tag,
  Layers,
  Play,
} from 'lucide-react';

export default function CreateProject() {
  const [projectName, setProjectName] = useState('');
  const [language, setLanguage] = useState('Python');
  const [framework, setFramework] = useState('');
  const [version, setVersion] = useState('1.0.0');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [description, setDescription] = useState('');
  const [sourceCodeFile, setSourceCodeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSourceCodeFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('project_name', projectName);
      formData.append('language', language);
      if (framework) formData.append('framework', framework);
      if (version) formData.append('version', version);
      if (repositoryUrl) formData.append('repository_url', repositoryUrl);
      if (description) formData.append('description', description);
      if (sourceCodeFile) formData.append('source_code_file', sourceCodeFile);

      const res = await projectApi.create(formData);
      navigate(`/analysis?project_id=${res.data.id}`);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to create project. Please check inputs.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/projects"
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create New Software Project</h1>
          <p className="text-slate-400 text-sm">Register a codebase repository for automated feature extraction</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <p className="text-xs text-rose-300 font-medium leading-relaxed">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-6">
        {/* Project Name */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">Project Name *</label>
          <div className="relative">
            <FileCode2 className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="text"
              required
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. ReliabilityAnalysisModule"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>
        </div>

        {/* Language, Framework & Version Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Language *</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            >
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript / Node.js</option>
              <option value="TypeScript">TypeScript</option>
              <option value="Java">Java</option>
              <option value="C++">C++</option>
              <option value="Go">Go</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Framework (Optional)</label>
            <input
              type="text"
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              placeholder="e.g. FastAPI / React"
              className="w-full px-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Version *</label>
            <div className="relative">
              <Tag className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                required
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                placeholder="v1.0.0"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
              />
            </div>
          </div>
        </div>

        {/* GitHub Repository URL */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">GitHub Repository URL (Optional)</label>
          <div className="relative">
            <GitBranch className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
            <input
              type="url"
              value={repositoryUrl}
              onChange={(e) => setRepositoryUrl(e.target.value)}
              placeholder="https://github.com/organization/repository"
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
            />
          </div>
        </div>

        {/* Source Code Archive Upload ZIP */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Upload ZIP Archive or Source Code File
          </label>
          <div className="relative border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-2xl p-6 text-center transition-colors bg-slate-950/40">
            <input
              type="file"
              accept=".zip,.py,.js,.ts,.java,.cpp,.go"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Upload className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
            {sourceCodeFile ? (
              <div className="space-y-1">
                <p className="text-sm font-semibold text-cyan-400">{sourceCodeFile.name}</p>
                <p className="text-xs text-slate-500">{(sourceCodeFile.size / 1024).toFixed(1)} KB archive</p>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-xs text-slate-300 font-medium">Click to upload ZIP file or drag & drop</p>
                <p className="text-[11px] text-slate-500">Supported formats: .ZIP, .PY, .JS, .TS, .JAVA, .CPP, .GO</p>
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">Description</label>
          <textarea
            rows="3"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief overview of software module responsibilities..."
            className="w-full p-4 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>

        {/* Submit Action Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-xl text-sm shadow-lg shadow-cyan-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {loading ? (
            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Create Project & Run Code Analysis</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}

