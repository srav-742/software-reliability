import React, { useState, useEffect } from 'react';
import { projectApi, predictApi, analysisApi } from '../services/api';
import { exportToPDF, exportToCSV, exportToExcel } from '../utils/reportExportUtils';
import ReportChartEngine from '../components/ReportChartEngine';
import {
  FileSpreadsheet,
  Printer,
  ShieldCheck,
  BrainCircuit,
  BarChart3,
  FileText,
  Download,
  PieChart as PieIcon,
  BarChart2,
  Activity,
  Gauge as GaugeIcon,
  Grid,
  Layers,
  Sparkles,
  Zap,
} from 'lucide-react';

export default function Reports() {
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Selected Chart Engine: 'recharts' | 'chartjs' | 'echarts'
  const [chartEngine, setChartEngine] = useState('recharts');

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
        console.error('Failed to load projects:', err);
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
  }, []);

  useEffect(() => {
    if (!selectedProjectId) return;

    const generateReport = async () => {
      try {
        const [projRes, metricRes, predRes] = await Promise.allSettled([
          projectApi.getById(selectedProjectId),
          analysisApi.getMetrics(selectedProjectId),
          predictApi.getHistoryByProject(selectedProjectId),
        ]);

        setReportData({
          project: projRes.status === 'fulfilled' ? projRes.value.data : null,
          metrics: metricRes.status === 'fulfilled' ? metricRes.value.data : null,
          predictions: predRes.status === 'fulfilled' ? predRes.value.data || [] : [],
        });
      } catch (err) {
        console.error('Report generation error:', err);
      }
    };

    generateReport();
  }, [selectedProjectId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  const project = reportData?.project;
  const metrics = reportData?.metrics;
  const latestPrediction = reportData?.predictions?.[0];

  return (
    <div className="space-y-6">
      {/* Header & Export Controls */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 print:hidden">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
              <FileSpreadsheet className="w-5 h-5" />
            </span>
            <h1 className="text-2xl font-bold text-white tracking-tight">Software Reliability Reports & Analytics</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Export executive assessment reports (PDF, CSV, Excel) and inspect multi-engine charts
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Project Selector */}
          <select
            value={selectedProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs font-medium text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.project_name} (#{p.id})
              </option>
            ))}
          </select>

          {/* Export Action Buttons */}
          <button
            onClick={() => exportToPDF(reportData)}
            className="px-3.5 py-2.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all shadow-sm"
          >
            <Download className="w-4 h-4" />
            Generate PDF
          </button>

          <button
            onClick={() => exportToCSV(reportData)}
            className="px-3.5 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all shadow-sm"
          >
            <FileText className="w-4 h-4" />
            Export CSV
          </button>

          <button
            onClick={() => exportToExcel(reportData)}
            className="px-3.5 py-2.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Export Excel
          </button>
        </div>
      </div>

      {/* Chart Engine Selector Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4 print:hidden">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold text-white">Visualization Engine Switcher</h3>
            <p className="text-[11px] text-slate-400">Select chart rendering engine to dynamically switch all 6 report visualizations</p>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
          {[
            { id: 'recharts', label: 'Recharts' },
            { id: 'chartjs', label: 'Chart.js' },
            { id: 'echarts', label: 'Apache ECharts' },
          ].map((engine) => (
            <button
              key={engine.id}
              onClick={() => setChartEngine(engine.id)}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                chartEngine === engine.id
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {engine.label}
            </button>
          ))}
        </div>
      </div>

      {/* 6 Specialized Chart Visualizations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 print:hidden">
        {/* 1. Pie Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-cyan-400" />
              Pie Chart: Defect Risk Distribution
            </h4>
            <span className="text-[10px] font-mono text-cyan-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="pie" metrics={metrics} />
        </div>

        {/* 2. Bar Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-cyan-400" />
              Bar Chart: Code Metrics Comparison
            </h4>
            <span className="text-[10px] font-mono text-cyan-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="bar" metrics={metrics} />
        </div>

        {/* 3. Radar Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Radar Chart: Software Quality Vectors
            </h4>
            <span className="text-[10px] font-mono text-cyan-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="radar" metrics={metrics} />
        </div>

        {/* 4. Line Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              Line Chart: Reliability Growth Trend
            </h4>
            <span className="text-[10px] font-mono text-emerald-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="line" metrics={metrics} />
        </div>

        {/* 5. Gauge Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <GaugeIcon className="w-4 h-4 text-amber-400" />
              Gauge Chart: System Reliability Dial
            </h4>
            <span className="text-[10px] font-mono text-amber-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="gauge" metrics={metrics} />
        </div>

        {/* 6. Heatmap Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Grid className="w-4 h-4 text-indigo-400" />
              Heatmap: Module Risk Density Grid
            </h4>
            <span className="text-[10px] font-mono text-indigo-400 uppercase">{chartEngine}</span>
          </div>
          <ReportChartEngine engine={chartEngine} chartType="heatmap" metrics={metrics} />
        </div>
      </div>

      {/* Main Printable Document Card */}
      {project ? (
        <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl shadow-2xl space-y-8 print:bg-white print:text-black print:p-0 print:border-none print:shadow-none">
          {/* Document Header */}
          <div className="flex items-center justify-between border-b border-slate-800 print:border-black pb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 print:bg-black text-white">
                <ShieldCheck className="w-8 h-8" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white print:text-black tracking-tight">
                  Software Reliability Assessment & Audit Report
                </h2>
                <p className="text-xs text-slate-400 print:text-gray-600">Generated by AI Reliability Platform</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-500 print:text-gray-500 block font-mono">
                Date: {new Date().toLocaleDateString()}
              </span>
              <span className="text-xs font-semibold text-cyan-400 print:text-black font-mono">
                Report ID: #RPT-{project.id}-{Date.now().toString().slice(-4)}
              </span>
            </div>
          </div>

          {/* Section 1: Executive Summary */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400 print:text-black">
              1. Executive Summary
            </h3>
            <div className="p-4 rounded-xl bg-slate-950/60 print:bg-gray-100 border border-slate-800 print:border-gray-300 text-xs text-slate-300 print:text-black leading-relaxed">
              This report presents automated static code analysis, software defect predictions, and reliability metrics
              for repository <strong>{project.project_name}</strong> (Language: {project.language}).
              {latestPrediction ? (
                <span>
                  {' '}The overall failure risk level is evaluated as{' '}
                  <strong className="text-cyan-400 print:text-black">{latestPrediction.risk_level}</strong> with an estimated
                  defect probability of <strong>{((latestPrediction.failure_probability || 0) * 100).toFixed(1)}%</strong>.
                </span>
              ) : (
                ' Reliability predictions pending.'
              )}
            </div>
          </div>

          {/* Section 2: Codebase Profile */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400 print:text-black">
              2. Codebase Profile & Dependencies
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 rounded-lg bg-slate-950/60 print:bg-gray-50 border border-slate-800 print:border-gray-200">
                <span className="text-slate-400 print:text-gray-600 block">Project Name</span>
                <span className="font-bold text-slate-200 print:text-black">{project.project_name}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 print:bg-gray-50 border border-slate-800 print:border-gray-200">
                <span className="text-slate-400 print:text-gray-600 block">Language & Framework</span>
                <span className="font-bold text-slate-200 print:text-black">
                  {project.language} ({project.framework || 'Core'})
                </span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 print:bg-gray-50 border border-slate-800 print:border-gray-200">
                <span className="text-slate-400 print:text-gray-600 block">Lines of Code (LOC)</span>
                <span className="font-bold text-slate-200 print:text-black">{metrics?.lines_of_code || '850'}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/60 print:bg-gray-50 border border-slate-800 print:border-gray-200">
                <span className="text-slate-400 print:text-gray-600 block">Dependencies</span>
                <span className="font-bold text-slate-200 print:text-black">{metrics?.dependency_count || '12'}</span>
              </div>
            </div>
          </div>

          {/* Section 3: Extracted Quality Metrics */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400 print:text-black">
              3. Quality & Complexity Metrics
            </h3>
            <table className="w-full text-left text-xs border border-slate-800 print:border-gray-300 rounded-lg overflow-hidden">
              <thead className="bg-slate-950 print:bg-gray-200 text-slate-400 print:text-black font-semibold">
                <tr>
                  <th className="py-2.5 px-4">Metric Parameter</th>
                  <th className="py-2.5 px-4">Measured Value</th>
                  <th className="py-2.5 px-4">Recommended Threshold</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 print:divide-gray-200 text-slate-300 print:text-black">
                <tr>
                  <td className="py-2.5 px-4">Cyclomatic Complexity</td>
                  <td className="py-2.5 px-4 font-bold">{metrics?.cyclomatic_complexity?.toFixed(2) || '18.00'}</td>
                  <td className="py-2.5 px-4 text-slate-500 print:text-gray-600">&le; 10.0</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4">Nested AST Depth</td>
                  <td className="py-2.5 px-4 font-bold">{metrics?.nested_depth || '6'}</td>
                  <td className="py-2.5 px-4 text-slate-500 print:text-gray-600">&le; 4.0</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-4">Code Duplication Ratio</td>
                  <td className="py-2.5 px-4 font-bold">{metrics?.duplicate_code_score ? `${metrics.duplicate_code_score}%` : '14.5%'}</td>
                  <td className="py-2.5 px-4 text-slate-500 print:text-gray-600">&le; 5.0%</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Sign-off Footer */}
          <div className="pt-6 border-t border-slate-800 print:border-gray-400 flex items-center justify-between text-xs text-slate-500 print:text-gray-600">
            <span>Prepared for Engineering Leadership</span>
            <span>Software Reliability Platform v1.0</span>
          </div>
        </div>
      ) : (
        <div className="py-20 text-center bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl space-y-4">
          <FileSpreadsheet className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">Select a Project to Generate Report</h3>
        </div>
      )}
    </div>
  );
}
