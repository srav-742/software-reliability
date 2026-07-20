import React from 'react';
import ReactECharts from 'echarts-for-react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip as ChartJSTooltip,
  Legend as ChartJSLegend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title,
} from 'chart.js';
import { Pie as ChartJSPie, Bar as ChartJSBar, Line as ChartJSLine, Radar as ChartJSRadar } from 'react-chartjs-2';
import {
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie as RePie,
  Cell as ReCell,
  BarChart as ReBarChart,
  Bar as ReBar,
  XAxis as ReXAxis,
  YAxis as ReYAxis,
  CartesianGrid as ReCartesianGrid,
  Tooltip as ReTooltip,
  Legend as ReLegend,
  LineChart as ReLineChart,
  Line as ReLine,
  RadarChart as ReRadarChart,
  Radar as ReRadar,
  PolarGrid as RePolarGrid,
  PolarAngleAxis as RePolarAngleAxis,
  PolarRadiusAxis as RePolarRadiusAxis,
} from 'recharts';

// Register Chart.js modules
ChartJS.register(
  ArcElement,
  ChartJSTooltip,
  ChartJSLegend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Title
);

export default function ReportChartEngine({ engine = 'recharts', chartType = 'pie', data, metrics }) {
  // --- Data Preparation ---
  const pieData = [
    { name: 'Low Risk', value: 45, color: '#10b981' },
    { name: 'Medium Risk', value: 30, color: '#f59e0b' },
    { name: 'High Risk', value: 18, color: '#f97316' },
    { name: 'Critical Risk', value: 7, color: '#ef4444' },
  ];

  const barData = [
    { metric: 'Complexity', value: metrics?.cyclomatic_complexity || 18, target: 10 },
    { metric: 'Nested Depth', value: metrics?.nested_depth || 6, target: 4 },
    { metric: 'Duplication %', value: metrics?.duplicate_code_score || 14.5, target: 5 },
    { metric: 'Dependencies', value: metrics?.dependency_count || 12, target: 10 },
    { metric: 'LOC (x100)', value: Math.round((metrics?.lines_of_code || 850) / 100), target: 5 },
  ];

  const radarData = [
    { subject: 'Maintainability', value: 78, fullMark: 100 },
    { subject: 'Reliability', value: 85, fullMark: 100 },
    { subject: 'Security', value: 92, fullMark: 100 },
    { subject: 'Testability', value: 65, fullMark: 100 },
    { subject: 'Performance', value: 88, fullMark: 100 },
    { subject: 'Complexity', value: 60, fullMark: 100 },
  ];

  const lineData = [
    { hour: '0h', failureRate: 0.045, reliability: 100 },
    { hour: '50h', failureRate: 0.032, reliability: 92 },
    { hour: '100h', failureRate: 0.021, reliability: 88 },
    { hour: '150h', failureRate: 0.015, reliability: 85 },
    { hour: '200h', failureRate: 0.009, reliability: 84 },
  ];

  const heatmapMatrix = [
    { module: 'Auth Service', complexity: 'High', bugs: 12, riskScore: 0.82 },
    { module: 'Payment Gateway', complexity: 'Critical', bugs: 18, riskScore: 0.94 },
    { module: 'Analytics Engine', complexity: 'Medium', bugs: 5, riskScore: 0.45 },
    { module: 'User Profile API', complexity: 'Low', bugs: 2, riskScore: 0.20 },
    { module: 'Database Layer', complexity: 'High', bugs: 9, riskScore: 0.75 },
  ];

  const reliabilityScore = 86.4;

  // ==========================================
  // 1. APACHE ECHARTS RENDER ENGINE
  // ==========================================
  if (engine === 'echarts') {
    let option = {};

    switch (chartType) {
      case 'pie':
        option = {
          backgroundColor: 'transparent',
          tooltip: { trigger: 'item' },
          legend: { top: '5%', left: 'center', textStyle: { color: '#94a3b8' } },
          series: [
            {
              name: 'Defect Risk Distribution',
              type: 'pie',
              radius: ['40%', '70%'],
              avoidLabelOverlap: false,
              itemStyle: { borderRadius: 10, borderColor: '#0f172a', borderWidth: 2 },
              label: { show: false },
              data: pieData.map((d) => ({ value: d.value, name: d.name, itemStyle: { color: d.color } })),
            },
          ],
        };
        break;

      case 'bar':
        option = {
          backgroundColor: 'transparent',
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: barData.map((d) => d.metric), axisLabel: { color: '#94a3b8' } },
          yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
          series: [
            { name: 'Current', data: barData.map((d) => d.value), type: 'bar', itemStyle: { color: '#38bdf8' } },
            { name: 'Target', data: barData.map((d) => d.target), type: 'bar', itemStyle: { color: '#10b981' } },
          ],
        };
        break;

      case 'radar':
        option = {
          backgroundColor: 'transparent',
          tooltip: {},
          radar: {
            indicator: radarData.map((d) => ({ name: d.subject, max: 100 })),
            axisName: { color: '#38bdf8' },
            splitArea: { areaStyle: { color: ['rgba(30,41,59,0.2)', 'rgba(15,23,42,0.4)'] } },
          },
          series: [
            {
              type: 'radar',
              data: [{ value: radarData.map((d) => d.value), name: 'Software Quality Profile' }],
              itemStyle: { color: '#38bdf8' },
              areaStyle: { color: 'rgba(56,189,248,0.2)' },
            },
          ],
        };
        break;

      case 'line':
        option = {
          backgroundColor: 'transparent',
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: lineData.map((d) => d.hour), axisLabel: { color: '#94a3b8' } },
          yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
          series: [
            {
              name: 'Reliability %',
              data: lineData.map((d) => d.reliability),
              type: 'line',
              smooth: true,
              itemStyle: { color: '#10b981' },
              areaStyle: { color: 'rgba(16,185,129,0.15)' },
            },
          ],
        };
        break;

      case 'gauge':
        option = {
          backgroundColor: 'transparent',
          series: [
            {
              type: 'gauge',
              startAngle: 180,
              endAngle: 0,
              min: 0,
              max: 100,
              pointer: { icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z', length: '12%', width: 10, offsetCenter: [0, '-60%'] },
              axisLine: {
                lineStyle: {
                  width: 18,
                  color: [
                    [0.3, '#ef4444'],
                    [0.7, '#f59e0b'],
                    [1, '#10b981'],
                  ],
                },
              },
              detail: { valueAnimation: true, formatter: '{value}%', color: '#38bdf8', fontSize: 24, offsetCenter: [0, '-10%'] },
              data: [{ value: reliabilityScore, name: 'System Reliability' }],
              title: { offsetCenter: [0, '30%'], textStyle: { color: '#94a3b8', fontSize: 12 } },
            },
          ],
        };
        break;

      case 'heatmap':
        option = {
          backgroundColor: 'transparent',
          tooltip: { position: 'top' },
          grid: { height: '60%', top: '10%' },
          xAxis: { type: 'category', data: ['Auth', 'Payment', 'Analytics', 'Profile', 'DB Layer'], axisLabel: { color: '#94a3b8' } },
          yAxis: { type: 'category', data: ['Bugs', 'Complexity'], axisLabel: { color: '#94a3b8' } },
          visualMap: { min: 0, max: 20, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%', inRange: { color: ['#0284c7', '#f59e0b', '#ef4444'] } },
          series: [
            {
              name: 'Risk Density',
              type: 'heatmap',
              data: [
                [0, 0, 12], [0, 1, 18],
                [1, 0, 18], [1, 1, 20],
                [2, 0, 5],  [2, 1, 8],
                [3, 0, 2],  [3, 1, 4],
                [4, 0, 9],  [4, 1, 15],
              ],
              label: { show: true, color: '#ffffff' },
            },
          ],
        };
        break;

      default:
        break;
    }

    return <ReactECharts option={option} style={{ height: '300px', width: '100%' }} />;
  }

  // ==========================================
  // 2. CHART.JS RENDER ENGINE
  // ==========================================
  if (engine === 'chartjs') {
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
      },
    };

    switch (chartType) {
      case 'pie':
        return (
          <div className="h-72 w-full flex items-center justify-center">
            <ChartJSPie
              data={{
                labels: pieData.map((d) => d.name),
                datasets: [
                  {
                    data: pieData.map((d) => d.value),
                    backgroundColor: pieData.map((d) => d.color),
                    borderColor: '#0f172a',
                    borderWidth: 2,
                  },
                ],
              }}
              options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94a3b8' } } } }}
            />
          </div>
        );

      case 'bar':
        return (
          <div className="h-72 w-full">
            <ChartJSBar
              data={{
                labels: barData.map((d) => d.metric),
                datasets: [
                  { label: 'Measured Value', data: barData.map((d) => d.value), backgroundColor: '#38bdf8' },
                  { label: 'Target Limit', data: barData.map((d) => d.target), backgroundColor: '#10b981' },
                ],
              }}
              options={commonOptions}
            />
          </div>
        );

      case 'radar':
        return (
          <div className="h-72 w-full flex items-center justify-center">
            <ChartJSRadar
              data={{
                labels: radarData.map((d) => d.subject),
                datasets: [
                  {
                    label: 'Quality Score',
                    data: radarData.map((d) => d.value),
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: { r: { ticks: { color: '#94a3b8', backdropColor: 'transparent' }, grid: { color: '#1e293b' }, pointLabels: { color: '#38bdf8' } } },
              }}
            />
          </div>
        );

      case 'line':
        return (
          <div className="h-72 w-full">
            <ChartJSLine
              data={{
                labels: lineData.map((d) => d.hour),
                datasets: [
                  {
                    label: 'Reliability Growth %',
                    data: lineData.map((d) => d.reliability),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.3,
                  },
                ],
              }}
              options={commonOptions}
            />
          </div>
        );

      case 'gauge':
      case 'heatmap':
        // Canvas fallback rendered via Custom SVG Gauge / Heatmap Grid for Chart.js mode
        return (
          <div className="h-72 w-full flex flex-col items-center justify-center p-4">
            <div className="relative w-44 h-44 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path className="text-slate-800" strokeWidth="3.8" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path className="text-cyan-400" strokeDasharray={`${reliabilityScore}, 100`} strokeWidth="3.8" strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <div className="absolute text-center">
                <span className="text-2xl font-bold text-white">{reliabilityScore}%</span>
                <span className="text-[10px] text-slate-400 block font-mono">Chart.js Gauge</span>
              </div>
            </div>
          </div>
        );

      default:
        break;
    }
  }

  // ==========================================
  // 3. RECHARTS RENDER ENGINE (Default)
  // ==========================================
  switch (chartType) {
    case 'pie':
      return (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RePieChart>
              <RePie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value">
                {pieData.map((entry, index) => (
                  <ReCell key={`cell-${index}`} fill={entry.color} />
                ))}
              </RePie>
              <ReTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
              <ReLegend wrapperStyle={{ color: '#94a3b8', fontSize: '12px' }} />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      );

    case 'bar':
      return (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ReBarChart data={barData}>
              <ReCartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <ReXAxis dataKey="metric" stroke="#64748b" fontSize={11} />
              <ReYAxis stroke="#64748b" fontSize={11} />
              <ReTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
              <ReLegend />
              <ReBar dataKey="value" fill="#38bdf8" name="Measured Value" radius={[4, 4, 0, 0]} />
              <ReBar dataKey="target" fill="#10b981" name="Target Limit" radius={[4, 4, 0, 0]} />
            </ReBarChart>
          </ResponsiveContainer>
        </div>
      );

    case 'radar':
      return (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ReRadarChart data={radarData}>
              <RePolarGrid stroke="#1e293b" />
              <RePolarAngleAxis dataKey="subject" stroke="#38bdf8" fontSize={11} />
              <RePolarRadiusAxis stroke="#64748b" fontSize={10} />
              <ReRadar name="Quality Vectors" dataKey="value" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.25} />
              <ReTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
            </ReRadarChart>
          </ResponsiveContainer>
        </div>
      );

    case 'line':
      return (
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ReLineChart data={lineData}>
              <ReCartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <ReXAxis dataKey="hour" stroke="#64748b" fontSize={11} />
              <ReYAxis stroke="#64748b" fontSize={11} />
              <ReTooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }} />
              <ReLine type="monotone" dataKey="reliability" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} name="Reliability %" />
            </ReLineChart>
          </ResponsiveContainer>
        </div>
      );

    case 'gauge':
      return (
        <div className="h-72 w-full flex flex-col items-center justify-center p-4">
          <div className="relative w-48 h-48 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path className="text-slate-800" strokeWidth="4" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              <path className="text-emerald-400" strokeDasharray={`${reliabilityScore}, 100`} strokeWidth="4" strokeLinecap="round" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            </svg>
            <div className="absolute text-center space-y-1">
              <span className="text-3xl font-extrabold text-white">{reliabilityScore}%</span>
              <span className="text-[10px] text-cyan-400 block font-semibold uppercase tracking-wider">Reliability Score</span>
            </div>
          </div>
        </div>
      );

    case 'heatmap':
      return (
        <div className="h-72 w-full p-4 space-y-3 overflow-y-auto">
          <div className="grid grid-cols-1 gap-2">
            {heatmapMatrix.map((item, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      item.riskScore > 0.8 ? 'bg-rose-500 animate-pulse' : item.riskScore > 0.5 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                  />
                  <div>
                    <h5 className="text-xs font-bold text-white">{item.module}</h5>
                    <span className="text-[10px] text-slate-400">Complexity Level: {item.complexity}</span>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs">
                  <span className="font-mono text-slate-300">{item.bugs} Bugs Observed</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                      item.riskScore > 0.8
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    }`}
                  >
                    Score: {item.riskScore.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    default:
      return null;
  }
}
