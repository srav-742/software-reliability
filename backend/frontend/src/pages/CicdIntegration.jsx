import React, { useState, useEffect } from 'react';
import { apiKeyApi, cicdApi, projectApi } from '../services/api';
import { 
  Key, 
  Terminal, 
  GitBranch, 
  GitCommit, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Copy, 
  Plus, 
  Trash2, 
  ShieldAlert, 
  ExternalLink,
  RefreshCw,
  FileCode
} from 'lucide-react';

export default function CicdIntegration() {
  const [apiKeys, setApiKeys] = useState([]);
  const [scans, setScans] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [loadingKeys, setLoadingKeys] = useState(true);
  const [loadingScans, setLoadingScans] = useState(true);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState(null);
  const [selectedScan, setSelectedScan] = useState(null);
  const [copiedKey, setCopiedKey] = useState(false);
  const [copiedYaml, setCopiedYaml] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    fetchData();
  }, [selectedProjectId]);

  const fetchData = async () => {
    try {
      setLoadingKeys(true);
      setLoadingScans(true);

      const keysRes = await apiKeyApi.getAll();
      setApiKeys(keysRes.data || []);

      const projRes = await projectApi.getAll();
      setProjects(projRes.data || []);

      const scansRes = await cicdApi.getScans(selectedProjectId || null);
      setScans(scansRes.data || []);
    } catch (err) {
      console.error('Error fetching CI/CD data:', err);
      setErrorMsg('Failed to load CI/CD integration details.');
    } finally {
      setLoadingKeys(false);
      setLoadingScans(false);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    try {
      const res = await apiKeyApi.create(newKeyName.trim());
      setCreatedKey(res.data);
      setNewKeyName('');
      fetchData();
    } catch (err) {
      console.error('Failed to create API key:', err);
      alert('Failed to generate API Key.');
    }
  };

  const handleRevokeKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to revoke this API key? Pipelines using it will fail.')) return;

    try {
      await apiKeyApi.revoke(keyId);
      fetchData();
    } catch (err) {
      console.error('Failed to revoke API key:', err);
      alert('Failed to revoke API key.');
    }
  };

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === 'key') {
      setCopiedKey(true);
      setTimeout(() => setCopiedKey(false), 2000);
    } else if (type === 'yaml') {
      setCopiedYaml(true);
      setTimeout(() => setCopiedYaml(false), 2000);
    }
  };

  const sampleYaml = `name: Software Reliability Quality Gate

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

jobs:
  reliability-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Software Reliability Scan
        env:
          RELIABILITY_API_URL: '${window.location.origin}'
          RELIABILITY_API_KEY: \${{ secrets.RELIABILITY_API_KEY }}
        run: |
          python cli/reliability_cli.py --warn-threshold 50 --fail-threshold 80`;

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-8 text-white shadow-xl border border-indigo-900/50">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400 border border-indigo-500/30">
                <Terminal className="h-6 w-6" />
              </div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">CI/CD Pipeline Integration</h1>
            </div>
            <p className="text-slate-300 max-w-2xl text-sm md:text-base">
              Integrate ML software reliability predictions directly into your GitHub Actions build pipelines. Block high-risk code pushes automatically before deployment.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-sm font-medium transition shadow-lg shadow-indigo-600/30"
          >
            <RefreshCw className="h-4 w-4" /> Refresh Data
          </button>
        </div>

        {/* Workflow Visualizer */}
        <div className="mt-8 pt-6 border-t border-indigo-800/40 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 text-center text-xs">
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex flex-col items-center">
            <span className="font-semibold text-indigo-300">1. Developer Push</span>
            <span className="text-slate-400 text-[11px] mt-1">Git commit to main/PR</span>
          </div>
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex flex-col items-center">
            <span className="font-semibold text-indigo-300">2. GitHub Actions</span>
            <span className="text-slate-400 text-[11px] mt-1">Triggers CLI runner</span>
          </div>
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex flex-col items-center">
            <span className="font-semibold text-indigo-300">3. ML Risk Engine</span>
            <span className="text-slate-400 text-[11px] mt-1">AST + Metrics prediction</span>
          </div>
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex flex-col items-center">
            <span className="font-semibold text-indigo-300">4. Policy Check</span>
            <span className="text-slate-400 text-[11px] mt-1">Risk &lt; 50% PASS | &gt; 80% FAIL</span>
          </div>
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50 flex flex-col items-center">
            <span className="font-semibold text-indigo-300">5. Quality Gate</span>
            <span className="text-slate-400 text-[11px] mt-1">Pass/Fail build exit code</span>
          </div>
        </div>
      </div>

      {/* API Key Management */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 mb-4">
            <Key className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">API Keys</h2>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            Generate secure tokens to authenticate your GitHub Actions workflows or automated scripts with the Reliability API.
          </p>

          <form onSubmit={handleCreateKey} className="space-y-3 mb-6">
            <input
              type="text"
              placeholder="e.g. GitHub Actions - Repo Name"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              required
            />
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded-lg text-sm font-medium transition"
            >
              <Plus className="h-4 w-4" /> Create API Key
            </button>
          </form>

          {/* Newly Created Key Modal Display */}
          {createdKey && (
            <div className="mb-6 p-4 bg-emerald-50 rounded-xl border border-emerald-200">
              <div className="flex items-center justify-between text-emerald-800 text-xs font-semibold mb-2">
                <span>NEW API KEY GENERATED</span>
                <button onClick={() => setCreatedKey(null)} className="text-emerald-600 hover:text-emerald-900">✕</button>
              </div>
              <p className="text-[11px] text-emerald-700 mb-2">Save this key in GitHub Secrets as <code>RELIABILITY_API_KEY</code>. You won't be able to see it again!</p>
              <div className="flex items-center gap-2 bg-white p-2 rounded border border-emerald-300">
                <code className="text-xs font-mono font-bold text-slate-800 truncate flex-1">{createdKey.raw_key}</code>
                <button
                  onClick={() => copyToClipboard(createdKey.raw_key, 'key')}
                  className="p-1 hover:bg-emerald-100 rounded text-emerald-700"
                  title="Copy Key"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
              {copiedKey && <span className="text-[10px] text-emerald-600 font-medium block mt-1">Copied to clipboard!</span>}
            </div>
          )}

          {/* Active Keys List */}
          <div className="space-y-3">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Keys</h3>
            {loadingKeys ? (
              <p className="text-xs text-slate-400">Loading API keys...</p>
            ) : apiKeys.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No active API keys found.</p>
            ) : (
              apiKeys.map((key) => (
                <div key={key.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <div>
                    <div className="font-semibold text-xs text-slate-800">{key.name}</div>
                    <div className="text-[11px] font-mono text-slate-500">{key.key_prefix}...</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      Created: {new Date(key.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button
                    onClick={() => handleRevokeKey(key.id)}
                    className="p-1.5 text-rose-500 hover:bg-rose-50 rounded-lg transition"
                    title="Revoke Key"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* GitHub Workflow Snippet */}
        <div className="lg:col-span-2 bg-slate-900 rounded-2xl p-6 text-white shadow-sm border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileCode className="h-5 w-5 text-indigo-400" />
                <h2 className="text-base font-bold">GitHub Actions Workflow Template</h2>
              </div>
              <button
                onClick={() => copyToClipboard(sampleYaml, 'yaml')}
                className="flex items-center gap-1 text-xs bg-slate-800 hover:bg-slate-700 text-indigo-300 px-3 py-1.5 rounded-lg border border-slate-700 transition"
              >
                <Copy className="h-3.5 w-3.5" />
                {copiedYaml ? 'Copied!' : 'Copy Workflow YAML'}
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Add this workflow to <code>.github/workflows/software-reliability-ci.yml</code> in your repository.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs overflow-x-auto text-indigo-200">
              <pre>{sampleYaml}</pre>
            </div>
          </div>

          <div className="mt-4 p-3 bg-indigo-950/60 rounded-xl border border-indigo-900/50 text-xs text-indigo-300 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-400 flex-shrink-0" />
              Build Policy: Risk &lt; 50% PASS, Risk 50%-80% WARN, Risk &gt; 80% FAIL (Exit Code 1)
            </span>
          </div>
        </div>
      </div>

      {/* Build Pipeline Execution History */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-900">Pipeline Execution History</h2>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Projects</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.project_name}</option>
              ))}
            </select>
          </div>
        </div>

        {loadingScans ? (
          <div className="py-12 text-center text-slate-400 text-sm">Loading scan pipeline history...</div>
        ) : scans.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">
            No CI/CD scans recorded yet. Trigger a scan from your GitHub Actions pipeline or CLI!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Commit SHA</th>
                  <th className="py-3 px-4">Branch</th>
                  <th className="py-3 px-4">Risk Score</th>
                  <th className="py-3 px-4">Failure Prob.</th>
                  <th className="py-3 px-4">Author</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {scans.map((scan) => {
                  let statusBadge = null;
                  if (scan.status === 'PASS') {
                    statusBadge = (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle className="h-3.5 w-3.5 text-emerald-600" /> PASS
                      </span>
                    );
                  } else if (scan.status === 'WARN') {
                    statusBadge = (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> WARN
                      </span>
                    );
                  } else {
                    statusBadge = (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        <XCircle className="h-3.5 w-3.5 text-rose-600" /> FAIL
                      </span>
                    );
                  }

                  return (
                    <tr key={scan.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4">{statusBadge}</td>
                      <td className="py-3 px-4 font-mono font-semibold text-slate-800">
                        <span className="flex items-center gap-1">
                          <GitCommit className="h-3.5 w-3.5 text-slate-400" />
                          {scan.commit_sha ? scan.commit_sha.substring(0, 7) : 'N/A'}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-600">{scan.branch || 'main'}</td>
                      <td className="py-3 px-4 font-bold text-slate-900">{scan.risk_score}%</td>
                      <td className="py-3 px-4 text-slate-600">{(scan.failure_probability * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 text-slate-600">{scan.author || 'Runner'}</td>
                      <td className="py-3 px-4 text-slate-500">{new Date(scan.created_at).toLocaleString()}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedScan(scan)}
                          className="text-indigo-600 hover:text-indigo-900 font-medium hover:underline text-xs"
                        >
                          View Report
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Report Modal */}
      {selectedScan && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 p-6 space-y-6">
            <div className="flex items-center justify-between border-b pb-4">
              <div>
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-bold text-slate-900">CI/CD Build Scan Report</h3>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    selectedScan.status === 'PASS'
                      ? 'bg-emerald-100 text-emerald-800'
                      : selectedScan.status === 'WARN'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-rose-100 text-rose-800'
                  }`}>
                    {selectedScan.status}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Scan ID #{selectedScan.id} • Commit: <code className="font-mono">{selectedScan.commit_sha ? selectedScan.commit_sha.substring(0,7) : 'N/A'}</code> ({selectedScan.branch || 'main'}) • {new Date(selectedScan.created_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => setSelectedScan(null)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Quick Metrics Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Risk Score</span>
                <p className="text-lg font-bold text-slate-900">{selectedScan.risk_score}%</p>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Failure Prob.</span>
                <p className="text-lg font-bold text-slate-900">{(selectedScan.failure_probability * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Pass Threshold</span>
                <p className="text-lg font-bold text-slate-900">&lt; {selectedScan.pass_threshold}%</p>
              </div>
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Fail Threshold</span>
                <p className="text-lg font-bold text-slate-900">&gt; {selectedScan.warn_threshold}%</p>
              </div>
            </div>

            {/* Markdown Log */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">GitHub Step Summary Output</h4>
              <div className="bg-slate-900 text-slate-100 p-4 rounded-xl font-mono text-xs overflow-x-auto leading-relaxed whitespace-pre-wrap">
                {selectedScan.report_markdown || `BUILD ASSESSMENT: ${selectedScan.status}\nRisk Score: ${selectedScan.risk_score}%\nFailure Probability: ${selectedScan.failure_probability}`}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t">
              <button
                onClick={() => setSelectedScan(null)}
                className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2 rounded-xl text-xs font-semibold transition"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
