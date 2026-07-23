import React, { useState, useEffect } from 'react';
import { projectApi, scanApi } from '../services/api';
import {
  KeyRound,
  Search,
  ShieldCheck,
  ShieldAlert,
  ShieldQuestion,
  FileCode2,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  Zap,
  RefreshCw,
  ChevronDown,
  Eye,
  FileSearch,
  Loader2,
  Lock,
  Unlock,
  History,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

// Provider display configurations
const PROVIDER_CONFIG = {
  openai: { label: 'OpenAI', color: '#10a37f', bg: 'from-emerald-500/20 to-green-500/10', border: 'border-emerald-500/30' },
  google_cloud: { label: 'Google Cloud', color: '#4285f4', bg: 'from-blue-500/20 to-blue-500/10', border: 'border-blue-500/30' },
  aws: { label: 'AWS', color: '#ff9900', bg: 'from-orange-500/20 to-amber-500/10', border: 'border-orange-500/30' },
  aws_secret: { label: 'AWS Secret', color: '#ff9900', bg: 'from-orange-500/20 to-amber-500/10', border: 'border-orange-500/30' },
  stripe: { label: 'Stripe', color: '#635bff', bg: 'from-violet-500/20 to-purple-500/10', border: 'border-violet-500/30' },
  stripe_publishable: { label: 'Stripe (Pub)', color: '#635bff', bg: 'from-violet-500/20 to-purple-500/10', border: 'border-violet-500/30' },
  github: { label: 'GitHub', color: '#f0f6fc', bg: 'from-slate-500/20 to-gray-500/10', border: 'border-slate-500/30' },
  sendgrid: { label: 'SendGrid', color: '#1a82e2', bg: 'from-sky-500/20 to-blue-500/10', border: 'border-sky-500/30' },
  twilio: { label: 'Twilio', color: '#f22f46', bg: 'from-red-500/20 to-rose-500/10', border: 'border-red-500/30' },
  slack: { label: 'Slack', color: '#e01e5a', bg: 'from-pink-500/20 to-rose-500/10', border: 'border-pink-500/30' },
  mailgun: { label: 'Mailgun', color: '#d44638', bg: 'from-red-500/20 to-orange-500/10', border: 'border-red-500/30' },
  huggingface: { label: 'HuggingFace', color: '#ffcc00', bg: 'from-yellow-500/20 to-amber-500/10', border: 'border-yellow-500/30' },
  azure: { label: 'Azure', color: '#0078d4', bg: 'from-blue-500/20 to-cyan-500/10', border: 'border-blue-500/30' },
  generic: { label: 'Generic', color: '#94a3b8', bg: 'from-slate-500/20 to-gray-500/10', border: 'border-slate-500/30' },
};

const STATUS_CONFIG = {
  valid: { label: 'Valid', icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', dot: 'bg-emerald-500' },
  invalid: { label: 'Invalid', icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30', dot: 'bg-red-500' },
  expired: { label: 'Expired', icon: Clock, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30', dot: 'bg-amber-500' },
  rate_limited: { label: 'Rate Limited', icon: AlertTriangle, color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', dot: 'bg-yellow-500' },
  unknown: { label: 'Unknown', icon: HelpCircle, color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/30', dot: 'bg-slate-500' },
};

const PIE_COLORS = ['#10b981', '#ef4444', '#64748b'];

export default function ApiKeyScanner() {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [scanResult, setScanResult] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState('');

  // Load projects on mount
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const res = await projectApi.getAll();
        const list = res.data || [];
        setProjects(list);
        if (list.length > 0) {
          setSelectedProjectId(list[0].id.toString());
        }
      } catch (err) {
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };
    loadProjects();
  }, []);

  // Load latest scan when project changes
  useEffect(() => {
    if (!selectedProjectId) return;
    const loadScan = async () => {
      try {
        const res = await scanApi.getResults(selectedProjectId);
        setScanResult(res.data);
      } catch {
        setScanResult(null);
      }
    };
    loadScan();
  }, [selectedProjectId]);

  // Trigger scan
  const handleScan = async () => {
    if (!selectedProjectId) return;
    setScanning(true);
    setError('');
    try {
      const res = await scanApi.scanKeys(selectedProjectId);
      setScanResult(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Scan failed. Ensure the project has uploaded source code.';
      setError(msg);
    } finally {
      setScanning(false);
    }
  };

  // Load scan history
  const handleLoadHistory = async () => {
    if (!selectedProjectId) return;
    try {
      const res = await scanApi.getHistory(selectedProjectId);
      setScanHistory(res.data || []);
      setShowHistory(true);
    } catch {
      setScanHistory([]);
    }
  };

  // Prepare chart data
  const pieData = scanResult ? [
    { name: 'Valid', value: scanResult.valid_keys },
    { name: 'Invalid', value: scanResult.invalid_keys },
    { name: 'Unknown', value: scanResult.unknown_keys },
  ].filter(d => d.value > 0) : [];

  const providerData = scanResult?.detected_keys?.reduce((acc, key) => {
    const provider = PROVIDER_CONFIG[key.provider]?.label || key.provider;
    const existing = acc.find(p => p.provider === provider);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ provider, count: 1, color: PROVIDER_CONFIG[key.provider]?.color || '#94a3b8' });
    }
    return acc;
  }, []) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-1">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 shadow-lg shadow-amber-500/20">
              <KeyRound className="w-6 h-6 text-white" />
            </div>
            API Key Scanner
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Detect and validate API keys embedded in your project source code
          </p>
        </div>
      </div>

      {/* Project Selection + Scan Controls */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-6">
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Select Project
            </label>
            <div className="relative">
              <select
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  setScanResult(null);
                  setShowHistory(false);
                  setError('');
                }}
              >
                <option value="">-- Choose a project --</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.project_name} ({p.language})
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>

          <button
            onClick={handleScan}
            disabled={!selectedProjectId || scanning}
            className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white shadow-lg shadow-amber-500/20 hover:shadow-amber-500/30"
          >
            {scanning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Scan for API Keys
              </>
            )}
          </button>

          <button
            onClick={handleLoadHistory}
            disabled={!selectedProjectId}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700"
          >
            <History className="w-4 h-4" />
            History
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
            <span className="text-red-300 text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Scanning Animation */}
      {scanning && (
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-8">
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-20 h-20 rounded-full border-4 border-slate-700 border-t-amber-500 animate-spin" />
              <FileSearch className="w-8 h-8 text-amber-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <div className="text-center">
              <p className="text-white font-semibold">Scanning project files...</p>
              <p className="text-slate-400 text-sm mt-1">
                Detecting API keys and validating with providers
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Scan Results */}
      {scanResult && !scanning && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SummaryCard
              title="Total Keys Found"
              value={scanResult.total_keys_found}
              icon={KeyRound}
              gradient="from-cyan-500/20 to-blue-500/10"
              borderColor="border-cyan-500/30"
              textColor="text-cyan-400"
            />
            <SummaryCard
              title="Valid Keys"
              value={scanResult.valid_keys}
              icon={ShieldCheck}
              gradient="from-emerald-500/20 to-green-500/10"
              borderColor="border-emerald-500/30"
              textColor="text-emerald-400"
            />
            <SummaryCard
              title="Invalid / Failed"
              value={scanResult.invalid_keys}
              icon={ShieldAlert}
              gradient="from-red-500/20 to-rose-500/10"
              borderColor="border-red-500/30"
              textColor="text-red-400"
            />
            <SummaryCard
              title="Unknown"
              value={scanResult.unknown_keys}
              icon={ShieldQuestion}
              gradient="from-slate-500/20 to-gray-500/10"
              borderColor="border-slate-500/30"
              textColor="text-slate-400"
            />
          </div>

          {/* Charts Row */}
          {scanResult.total_keys_found > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Status Pie Chart */}
              <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-6">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  Key Status Distribution
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                        color: '#e2e8f0',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-6 mt-2">
                  {pieData.map((d, idx) => (
                    <div key={d.name} className="flex items-center gap-2 text-xs text-slate-300">
                      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: PIE_COLORS[idx % PIE_COLORS.length] }} />
                      {d.name}: {d.value}
                    </div>
                  ))}
                </div>
              </div>

              {/* Provider Bar Chart */}
              <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-6">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <FileCode2 className="w-4 h-4 text-cyan-400" />
                  Keys by Provider
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={providerData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis type="category" dataKey="provider" stroke="#94a3b8" width={90} tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                        color: '#e2e8f0',
                      }}
                    />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {providerData.map((entry, idx) => (
                        <Cell key={idx} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Detailed Results Table */}
          {scanResult.detected_keys && scanResult.detected_keys.length > 0 && (
            <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
                <h3 className="text-white font-semibold flex items-center gap-2">
                  <Eye className="w-4 h-4 text-cyan-400" />
                  Detected API Keys
                </h3>
                <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full">
                  {scanResult.detected_keys.length} keys found
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-800/30">
                      <th className="text-left px-6 py-3 text-slate-400 font-medium">Provider</th>
                      <th className="text-left px-6 py-3 text-slate-400 font-medium">Masked Key</th>
                      <th className="text-left px-6 py-3 text-slate-400 font-medium">File</th>
                      <th className="text-center px-6 py-3 text-slate-400 font-medium">Line</th>
                      <th className="text-center px-6 py-3 text-slate-400 font-medium">Status</th>
                      <th className="text-center px-6 py-3 text-slate-400 font-medium">Chance to Fail</th>
                      <th className="text-left px-6 py-3 text-slate-400 font-medium">Risk Analysis</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scanResult.detected_keys.map((key) => {
                      const providerConf = PROVIDER_CONFIG[key.provider] || PROVIDER_CONFIG.generic;
                      const statusConf = STATUS_CONFIG[key.status] || STATUS_CONFIG.unknown;
                      const StatusIcon = statusConf.icon;

                      return (
                        <tr key={key.id} className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors">
                          {/* Provider */}
                          <td className="px-6 py-3">
                            <span
                              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-gradient-to-r ${providerConf.bg} ${providerConf.border} border`}
                              style={{ color: providerConf.color }}
                            >
                              {providerConf.label}
                            </span>
                          </td>

                          {/* Masked Key */}
                          <td className="px-6 py-3">
                            <code className="text-xs font-mono text-slate-300 bg-slate-800 px-2.5 py-1 rounded-md inline-flex items-center gap-1.5">
                              <Lock className="w-3 h-3 text-slate-500" />
                              {key.key_masked}
                            </code>
                          </td>

                          {/* File Path */}
                          <td className="px-6 py-3">
                            <span className="text-xs text-slate-300 flex items-center gap-1.5">
                              <FileCode2 className="w-3 h-3 text-slate-500 shrink-0" />
                              <span className="truncate max-w-[200px]" title={key.file_path}>
                                {key.file_path}
                              </span>
                            </span>
                          </td>

                          {/* Line Number */}
                          <td className="px-6 py-3 text-center">
                            <span className="text-xs text-slate-400 font-mono">
                              L{key.line_number}
                            </span>
                          </td>

                          {/* Status Badge */}
                          <td className="px-6 py-3 text-center">
                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusConf.bg} ${statusConf.border} border ${statusConf.color}`}>
                              <StatusIcon className="w-3 h-3" />
                              {statusConf.label}
                            </span>
                          </td>

                          {/* Chance to Fail Progress Bar */}
                          <td className="px-6 py-3 text-center">
                            <div className="flex flex-col items-center gap-1 min-w-[120px]">
                              <div className="flex items-center justify-between w-full text-xs font-semibold">
                                <span className={`
                                  ${key.risk_level === 'critical' ? 'text-red-400' : ''}
                                  ${key.risk_level === 'high' ? 'text-orange-400' : ''}
                                  ${key.risk_level === 'medium' ? 'text-yellow-400' : ''}
                                  ${key.risk_level === 'low' ? 'text-emerald-400' : ''}
                                `}>
                                  {key.risk_level.toUpperCase()}
                                </span>
                                <span className="text-slate-300 font-mono">
                                  {Math.round(key.failure_chance * 100)}%
                                </span>
                              </div>
                              <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden border border-slate-700/50">
                                <div
                                  className={`h-full rounded-full transition-all duration-500 ${
                                    key.risk_level === 'critical' ? 'bg-gradient-to-r from-red-600 to-rose-500' :
                                    key.risk_level === 'high' ? 'bg-gradient-to-r from-orange-500 to-amber-400' :
                                    key.risk_level === 'medium' ? 'bg-gradient-to-r from-yellow-500 to-yellow-400' :
                                    'bg-gradient-to-r from-emerald-500 to-green-400'
                                  }`}
                                  style={{ width: `${key.failure_chance * 100}%` }}
                                />
                              </div>
                            </div>
                          </td>

                          {/* Risk Analysis Reasons */}
                          <td className="px-6 py-3">
                            <span className="text-xs text-slate-300 block max-w-[280px]">
                              {key.error_message ? (
                                <div className="space-y-1">
                                  {key.error_message.split(' | ').map((reason, i) => (
                                    <div key={i} className="flex items-start gap-1">
                                      <span className="text-slate-500 mt-0.5">•</span>
                                      <span>{reason}</span>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <span className="text-slate-500">—</span>
                              )}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* No Keys Found State */}
          {scanResult.total_keys_found === 0 && scanResult.scan_status === 'completed' && (
            <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-8">
              <div className="flex flex-col items-center gap-4 text-center">
                <div className="p-4 rounded-full bg-emerald-500/10 border border-emerald-500/30">
                  <ShieldCheck className="w-10 h-10 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-white font-semibold text-lg">No API Keys Detected</h3>
                  <p className="text-slate-400 text-sm mt-1 max-w-md">
                    Great news! No embedded API keys were found in your project source code.
                    Your project follows good security practices.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Scan Timestamp */}
          <div className="flex justify-end">
            <p className="text-xs text-slate-500 flex items-center gap-1.5">
              <Clock className="w-3 h-3" />
              Scanned: {scanResult.scanned_at ? new Date(scanResult.scanned_at).toLocaleString() : 'N/A'}
            </p>
          </div>
        </>
      )}

      {/* No Project Selected State */}
      {!selectedProjectId && !scanning && (
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-8">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="p-4 rounded-full bg-slate-800 border border-slate-700">
              <FileSearch className="w-10 h-10 text-slate-400" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-lg">Select a Project</h3>
              <p className="text-slate-400 text-sm mt-1 max-w-md">
                Choose a project from the dropdown above and click "Scan for API Keys"
                to detect and validate API keys in the source code.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Scan History Modal */}
      {showHistory && (
        <div className="bg-slate-900/80 rounded-xl border border-slate-800 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              Scan History
            </h3>
            <button
              onClick={() => setShowHistory(false)}
              className="text-slate-400 hover:text-white text-xs"
            >
              Close
            </button>
          </div>

          {scanHistory.length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-sm">
              No scan history found for this project.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-800/30">
                    <th className="text-left px-6 py-3 text-slate-400 font-medium">Date</th>
                    <th className="text-center px-6 py-3 text-slate-400 font-medium">Total</th>
                    <th className="text-center px-6 py-3 text-slate-400 font-medium">Valid</th>
                    <th className="text-center px-6 py-3 text-slate-400 font-medium">Invalid</th>
                    <th className="text-center px-6 py-3 text-slate-400 font-medium">Unknown</th>
                    <th className="text-center px-6 py-3 text-slate-400 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {scanHistory.map((scan) => (
                    <tr key={scan.id} className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors">
                      <td className="px-6 py-3 text-slate-300 text-xs">
                        {scan.scanned_at ? new Date(scan.scanned_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-6 py-3 text-center text-cyan-400 font-mono">{scan.total_keys_found}</td>
                      <td className="px-6 py-3 text-center text-emerald-400 font-mono">{scan.valid_keys}</td>
                      <td className="px-6 py-3 text-center text-red-400 font-mono">{scan.invalid_keys}</td>
                      <td className="px-6 py-3 text-center text-slate-400 font-mono">{scan.unknown_keys}</td>
                      <td className="px-6 py-3 text-center">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                          scan.scan_status === 'completed'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-red-500/10 text-red-400 border border-red-500/30'
                        }`}>
                          {scan.scan_status === 'completed' ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          {scan.scan_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Reusable Summary Card Component
function SummaryCard({ title, value, icon: Icon, gradient, borderColor, textColor }) {
  return (
    <div className={`bg-slate-900/80 rounded-xl border ${borderColor} p-5 bg-gradient-to-br ${gradient}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">{title}</p>
          <p className={`text-3xl font-bold mt-1 ${textColor}`}>{value}</p>
        </div>
        <div className={`p-3 rounded-lg bg-slate-800/50 border ${borderColor}`}>
          <Icon className={`w-6 h-6 ${textColor}`} />
        </div>
      </div>
    </div>
  );
}
