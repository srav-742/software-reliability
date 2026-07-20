import React, { useState, useEffect } from 'react';
import { trainApi, modelApi } from '../services/api';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  Award,
  Sparkles,
  Zap,
  Check,
  RotateCw,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const ALL_ALGORITHMS = [
  'CatBoost',
  'XGBoost',
  'LightGBM',
  'Random Forest',
  'Support Vector Machine (SVM)',
  'Logistic Regression',
  'Neural Network (MLP)',
];

export default function Training() {
  const [selectedAlgos, setSelectedAlgos] = useState([...ALL_ALGORITHMS]);
  const [testSize, setTestSize] = useState(0.2);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [models, setModels] = useState([]);
  const [activeModel, setActiveModel] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [modelsRes, activeRes, histRes] = await Promise.allSettled([
        modelApi.getModels(),
        modelApi.getActiveModel(),
        trainApi.getHistory(),
      ]);

      if (modelsRes.status === 'fulfilled') setModels(modelsRes.value.data || []);
      if (activeRes.status === 'fulfilled') setActiveModel(activeRes.value.data);
      if (histRes.status === 'fulfilled') setHistory(histRes.value.data || []);
    } catch (err) {
      console.error('Failed to load training data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const toggleAlgorithm = (algo) => {
    if (selectedAlgos.includes(algo)) {
      if (selectedAlgos.length === 1) return; // Keep at least 1
      setSelectedAlgos(selectedAlgos.filter((a) => a !== algo));
    } else {
      setSelectedAlgos([...selectedAlgos, algo]);
    }
  };

  const handleStartTraining = async () => {
    setTraining(true);
    setError('');
    setTrainResult(null);

    try {
      const res = await trainApi.trainModels({
        algorithms: selectedAlgos,
        test_size: testSize,
      });
      setTrainResult(res.data);
      alert('Training completed successfully! Best model saved.');
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Training pipeline execution failed.');
    } finally {
      setTraining(false);
    }
  };

  const handleActivateModel = async (modelId) => {
    try {
      await modelApi.activateModel(modelId);
      alert('Model activated for inference!');
      loadData();
    } catch (err) {
      alert('Activation failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Prepare chart comparison data
  const comparisonData = (trainResult?.all_results || models).map((item) => {
    const metrics = item.metrics || item;
    return {
      name: item.algorithm || item.model_name || 'Model',
      F1: Number(((metrics.f1_score || metrics.test_f1 || 0) * 100).toFixed(1)),
      Accuracy: Number(((metrics.accuracy || metrics.test_accuracy || 0) * 100).toFixed(1)),
      AUC: Number(((metrics.roc_auc || metrics.test_roc_auc || 0) * 100).toFixed(1)),
    };
  });

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
          <h1 className="text-2xl font-bold text-white tracking-tight">Machine Learning Training & Registry</h1>
          <p className="text-slate-400 text-sm">Train 7 distinct algorithms, evaluate performance metrics, and activate models</p>
        </div>

        <button
          onClick={handleStartTraining}
          disabled={training || selectedAlgos.length === 0}
          className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          {training ? (
            <RotateCw className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {training ? 'Training 7 Models...' : 'Start Training Pipeline'}
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <p className="text-xs text-rose-300 font-medium leading-relaxed">{error}</p>
        </div>
      )}

      {/* Algorithm Selection Grid */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white">Algorithms Enrolled for Benchmarking</h3>
            <p className="text-xs text-slate-400">Select which ML models to train during the next run</p>
          </div>
          <span className="text-xs text-cyan-400 font-mono font-semibold">
            {selectedAlgos.length} of {ALL_ALGORITHMS.length} Selected
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {ALL_ALGORITHMS.map((algo) => {
            const isSelected = selectedAlgos.includes(algo);
            return (
              <button
                key={algo}
                type="button"
                onClick={() => toggleAlgorithm(algo)}
                className={`p-3 rounded-xl border text-left text-xs font-semibold transition-all flex items-center justify-between ${
                  isSelected
                    ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300 shadow-sm'
                    : 'bg-slate-950/40 border-slate-800 text-slate-500 hover:text-slate-300'
                }`}
              >
                <span>{algo}</span>
                {isSelected && <Check className="w-4 h-4 text-cyan-400 shrink-0" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Training Results & Comparison Charts */}
      {comparisonData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Comparative Performance Chart */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white">Algorithm Accuracy & F1 Benchmarks</h3>
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                  <Bar dataKey="F1" fill="#06b6d4" radius={[4, 4, 0, 0]} name="F1 Score %" />
                  <Bar dataKey="Accuracy" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Accuracy %" />
                  <Bar dataKey="AUC" fill="#10b981" radius={[4, 4, 0, 0]} name="ROC-AUC %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Active Model & Best Champion Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center gap-2 text-cyan-400 mb-2">
                <Award className="w-5 h-5" />
                <span className="text-xs font-semibold uppercase tracking-wider">Champion Model</span>
              </div>
              <h3 className="text-xl font-bold text-white">
                {trainResult?.best_algorithm || activeModel?.algorithm || 'CatBoost'}
              </h3>
              <p className="text-xs text-slate-400 mt-1">Highest F1 Score on test set cross-validation</p>
            </div>

            <div className="space-y-3 py-4 border-y border-slate-800">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Best F1 Score:</span>
                <span className="font-bold text-cyan-400">
                  {trainResult
                    ? `${(trainResult.best_metrics.f1_score * 100).toFixed(1)}%`
                    : activeModel?.test_f1
                    ? `${(activeModel.test_f1 * 100).toFixed(1)}%`
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Accuracy:</span>
                <span className="font-bold text-slate-200">
                  {trainResult
                    ? `${(trainResult.best_metrics.accuracy * 100).toFixed(1)}%`
                    : activeModel?.test_accuracy
                    ? `${(activeModel.test_accuracy * 100).toFixed(1)}%`
                    : 'N/A'}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-cyan-950/40 border border-cyan-800/40 text-xs text-cyan-300 flex items-center gap-2">
              <Zap className="w-4 h-4 shrink-0 text-cyan-400" />
              <span>Model artifacts serialized to disk & inference loader.</span>
            </div>
          </div>
        </div>
      )}

      {/* Model Registry List Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm space-y-4">
        <h3 className="text-base font-bold text-white">Model Registry & Version Management</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-3 px-4">Model ID / Name</th>
                <th className="py-3 px-4">Accuracy</th>
                <th className="py-3 px-4">F1 Score</th>
                <th className="py-3 px-4">ROC-AUC</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {models.map((model) => {
                const isActive = activeModel?.id === model.id || model.is_active;
                return (
                  <tr key={model.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-200">
                      {model.algorithm || model.model_name}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-semibold">
                      {((model.test_accuracy || model.accuracy || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-cyan-400 font-bold">
                      {((model.test_f1 || model.f1_score || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400 font-semibold">
                      {((model.test_roc_auc || model.roc_auc || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3.5 px-4">
                      {isActive ? (
                        <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase">
                          Active Inference
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 text-[10px]">
                          Standby
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      {!isActive && (
                        <button
                          onClick={() => handleActivateModel(model.id)}
                          className="px-3 py-1 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 rounded-lg text-xs font-semibold border border-cyan-500/30 transition-colors"
                        >
                          Activate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
              {models.length === 0 && (
                <tr>
                  <td colSpan="6" className="py-8 text-center text-slate-500 italic">
                    No models in registry. Click "Start Training Pipeline" above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
