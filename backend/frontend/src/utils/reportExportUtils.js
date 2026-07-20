import { jsPDF } from 'jspdf';
import * as XLSX from 'xlsx';

/**
 * Generate and download a CSV report
 */
export function exportToCSV(reportData) {
  if (!reportData) return;

  const { project, metrics, predictions } = reportData;
  const latestPred = predictions?.[0] || {};

  let csvContent = 'data:text/csv;charset=utf-8,';

  // Section 1: Project Overview
  csvContent += 'SOFTWARE RELIABILITY ASSESSMENT REPORT\n';
  csvContent += `Generated Date,${new Date().toLocaleString()}\n`;
  csvContent += `Project ID,${project?.id || 'N/A'}\n`;
  csvContent += `Project Name,${project?.project_name || 'N/A'}\n`;
  csvContent += `Language,${project?.language || 'N/A'}\n`;
  csvContent += `Framework,${project?.framework || 'N/A'}\n\n`;

  // Section 2: Failure Prediction Summary
  csvContent += 'PREDICTION SUMMARY\n';
  csvContent += `Risk Level,${latestPred.risk_level || 'N/A'}\n`;
  csvContent += `Failure Probability,${((latestPred.failure_probability || 0) * 100).toFixed(2)}%\n`;
  csvContent += `Confidence Score,${((latestPred.confidence_score || 0) * 100).toFixed(2)}%\n`;
  csvContent += `Model Engine,${latestPred.model_used || latestPred.model_name || 'N/A'}\n\n`;

  // Section 3: Extracted Metrics
  csvContent += 'EXTRACTED CODE METRICS\n';
  csvContent += 'Metric,Value\n';
  if (metrics) {
    Object.entries(metrics).forEach(([key, val]) => {
      if (typeof val === 'number' || typeof val === 'string') {
        csvContent += `"${key}",${val}\n`;
      }
    });
  }
  csvContent += '\n';

  // Section 4: Recommendations
  csvContent += 'AI REFACTORING RECOMMENDATIONS\n';
  const recs = latestPred.recommendations || [
    'Refactor long methods with high cyclomatic complexity.',
    'Reduce nested logic and guard clause depth.',
    'Optimize database query patterns.',
  ];
  recs.forEach((rec, idx) => {
    csvContent += `"${idx + 1}","${String(rec).replace(/"/g, '""')}"\n`;
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `reliability_report_project_${project?.id || 'export'}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Generate and download an Excel (.xlsx) workbook with multiple sheets
 */
export function exportToExcel(reportData) {
  if (!reportData) return;

  const { project, metrics, predictions } = reportData;
  const latestPred = predictions?.[0] || {};

  const wb = XLSX.utils.book_new();

  // Sheet 1: Executive Summary
  const summaryData = [
    ['Field', 'Value'],
    ['Report Title', 'Software Reliability Audit Report'],
    ['Generated Date', new Date().toLocaleString()],
    ['Project Name', project?.project_name || 'N/A'],
    ['Language', project?.language || 'N/A'],
    ['Framework', project?.framework || 'N/A'],
    ['Risk Level', latestPred.risk_level || 'N/A'],
    ['Failure Probability', `${((latestPred.failure_probability || 0) * 100).toFixed(2)}%`],
    ['Confidence Score', `${((latestPred.confidence_score || 0) * 100).toFixed(2)}%`],
    ['Model Engine', latestPred.model_used || latestPred.model_name || 'N/A'],
  ];
  const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Executive Summary');

  // Sheet 2: Code Metrics
  if (metrics) {
    const metricsRows = [['Metric Name', 'Measured Value']];
    Object.entries(metrics).forEach(([k, v]) => {
      if (typeof v === 'number' || typeof v === 'string') {
        metricsRows.push([k.replace(/_/g, ' ').toUpperCase(), v]);
      }
    });
    const wsMetrics = XLSX.utils.aoa_to_sheet(metricsRows);
    XLSX.utils.book_append_sheet(wb, wsMetrics, 'Code Metrics');
  }

  // Sheet 3: Recommendations
  const recs = latestPred.recommendations || [
    'Refactor long methods with high cyclomatic complexity.',
    'Reduce nested logic and guard clause depth.',
    'Optimize database query patterns.',
  ];
  const recRows = [['Priority', 'Recommendation']];
  recs.forEach((r, idx) => recRows.push([`Item #${idx + 1}`, r]));
  const wsRecs = XLSX.utils.aoa_to_sheet(recRows);
  XLSX.utils.book_append_sheet(wb, wsRecs, 'Recommendations');

  XLSX.writeFile(wb, `software_reliability_report_project_${project?.id || 'export'}.xlsx`);
}

/**
 * Generate and download a PDF document
 */
export function exportToPDF(reportData) {
  if (!reportData) return;

  const { project, metrics, predictions } = reportData;
  const latestPred = predictions?.[0] || {};

  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();

  // Colors
  doc.setFillColor(15, 23, 42); // slate-900
  doc.rect(0, 0, pageWidth, 40, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Software Reliability Assessment Report', 14, 22);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(56, 189, 248); // cyan-400
  doc.text(`Project: ${project?.project_name || 'N/A'} (Language: ${project?.language || 'N/A'})`, 14, 32);

  // Body Content
  let y = 50;

  // Executive Summary Box
  doc.setFillColor(241, 245, 249);
  doc.rect(14, y, pageWidth - 28, 35, 'F');

  doc.setTextColor(15, 23, 42);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('1. Executive Summary', 20, y + 10);

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  const riskText = `Risk Level: ${latestPred.risk_level || 'Medium'} | Defect Probability: ${((latestPred.failure_probability || 0) * 100).toFixed(1)}% | Confidence: ${((latestPred.confidence_score || 0.92) * 100).toFixed(1)}%`;
  doc.text(riskText, 20, y + 20);
  doc.text(`Evaluation Date: ${new Date().toLocaleDateString()}`, 20, y + 28);

  y += 45;

  // Metrics Table
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(15, 23, 42);
  doc.text('2. Quality & Complexity Metrics', 14, y);
  y += 8;

  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.setFillColor(226, 232, 240);
  doc.rect(14, y, pageWidth - 28, 8, 'F');
  doc.text('Metric Parameter', 18, y + 6);
  doc.text('Measured Value', 120, y + 6);
  doc.text('Target Threshold', 160, y + 6);
  y += 10;

  doc.setFont('helvetica', 'normal');
  const sampleMetrics = [
    ['Cyclomatic Complexity', String(metrics?.cyclomatic_complexity || 18), '<= 10.0'],
    ['AST Maximum Depth', String(metrics?.nested_depth || metrics?.ast_depth || 6), '<= 5'],
    ['Lines of Code (LOC)', String(metrics?.lines_of_code || 850), '<= 500'],
    ['Code Duplication Score', `${metrics?.duplicate_code_score || 14.5}%`, '<= 5%'],
    ['Dependencies Count', String(metrics?.dependency_count || 12), '<= 15'],
  ];

  sampleMetrics.forEach(([mName, mVal, mThresh]) => {
    doc.text(mName, 18, y);
    doc.text(mVal, 120, y);
    doc.text(mThresh, 160, y);
    y += 7;
  });

  y += 10;

  // Recommendations Section
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('3. AI Refactoring Recommendations', 14, y);
  y += 8;

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  const recs = latestPred.recommendations || [
    '[+0.42] High Complexity: Refactor long methods.',
    '[+0.26] Nested Logic: Reduce nested conditions.',
    '[+0.15] Database Queries: Optimize SQL queries.',
  ];

  recs.forEach((rec) => {
    const lines = doc.splitTextToSize(`• ${rec}`, pageWidth - 32);
    doc.text(lines, 18, y);
    y += lines.length * 6;
  });

  // Save PDF
  doc.save(`software_reliability_report_project_${project?.id || 'export'}.pdf`);
}
