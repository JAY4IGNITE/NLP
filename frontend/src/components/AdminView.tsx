import React, { useState, useEffect } from 'react';
import {
  Shield, FileText, AlertTriangle, BarChart3, CheckCircle2,
  RefreshCw, Check, X, FileCheck
} from 'lucide-react';
import { api } from '../api';
import type { ExtractionIssue } from '../types';

interface AdminViewProps {
  user: any;
  onOpenLogin?: () => void;
}

export const AdminView: React.FC<AdminViewProps> = ({ user, onOpenLogin }) => {
  const [activeSubTab, setActiveSubTab] = useState<'documents' | 'issues' | 'metrics'>('documents');
  const [issues, setIssues] = useState<ExtractionIssue[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [_loading, setLoading] = useState<boolean>(true);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState<string>('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const [loadError, setLoadError] = useState('');
  const [actionError, setActionError] = useState('');
  const [documents, setDocuments] = useState<{ id: string; name: string; file: string; pages: number; status: string }[]>([]);
  const [documentError, setDocumentError] = useState('');

  useEffect(() => {
    let cancelled = false;
    fetch('http://localhost:8000/api/v1/admin/documents')
      .then(response => { if (!response.ok) throw new Error('Document registry unavailable'); return response.json(); })
      .then(records => { if (!cancelled) setDocuments(records.map((record: { doc_id: string; department_code: string; file_name: string; total_pages: number; status: string }) => ({
        id: record.doc_id, name: record.department_code, file: record.file_name, pages: record.total_pages, status: record.status,
      }))); })
      .catch(() => { if (!cancelled) setDocumentError('The document registry is unavailable. Reopen this view to retry.'); });
    return () => { cancelled = true; };
  }, []);

  const loadData = () => {
    setLoading(true);
    setLoadError('');
    Promise.all([
      api.getExtractionIssues().catch(() => { setLoadError('Extraction issues could not be loaded. Use refresh to try again.'); return []; }),
      api.getEvaluations().catch(() => null)
    ]).then(([issuesData, metricsData]) => {
      setIssues(issuesData);
      setMetrics(metricsData);
      setLoading(false);
    });
  };

  const handleResolveIssue = async (id: number, status: 'resolved' | 'suppressed') => {
    if (!user || !user.token) {
      if (onOpenLogin) onOpenLogin();
      return;
    }
    setActionError('');
    try {
      await api.updateExtractionIssue(id, status, resolutionNotes || 'Reviewed by department administrator', user.token);
      setActionSuccess(`Issue #${id} updated to ${status}`);
      setResolvingId(null);
      setResolutionNotes('');
      loadData();
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err: any) {
      setActionError(err.message || 'Failed to update issue');
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const percentage = (value: unknown) => typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : 'Unavailable';

  return (
    <div className="workspace-view view-enter space-y-6 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-[var(--ink)]/10">
        <div>
          <div className="text-[11px] font-bold text-blue-400 tracking-wider uppercase flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" /> Institutional Administration
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--ink)] mt-1">
            Curriculum Governance & Provenance
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            Audit indexed departmental handbooks, resolve extraction ambiguities, and inspect RAG benchmark metrics.
          </p>
        </div>
      </div>

      {actionError && <div role="alert" className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">{actionError}</div>}
      {actionSuccess && (
        <div role="status" className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" /> {actionSuccess}
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-1.5 border-b border-[var(--ink)]/10 pb-2">
        <button
          aria-pressed={activeSubTab === 'documents'}
          onClick={() => setActiveSubTab('documents')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'documents'
              ? 'bg-blue-600 text-[var(--paper)] shadow-md shadow-blue-600/30 ring-1 ring-white/20'
              : 'glass-pill text-slate-300 hover:text-[var(--ink)]'
          }`}
        >
          <FileText className="w-3.5 h-3.5" /> Documents ({documents.length})
        </button>
        <button
          aria-pressed={activeSubTab === 'issues'}
          onClick={() => setActiveSubTab('issues')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'issues'
              ? 'bg-blue-600 text-[var(--paper)] shadow-md shadow-blue-600/30 ring-1 ring-white/20'
              : 'glass-pill text-slate-300 hover:text-[var(--ink)]'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          Discrepancy Review ({issues.filter(i => i.status === 'pending').length})
        </button>
        <button
          aria-pressed={activeSubTab === 'metrics'}
          onClick={() => setActiveSubTab('metrics')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'metrics'
              ? 'bg-blue-600 text-[var(--paper)] shadow-md shadow-blue-600/30 ring-1 ring-white/20'
              : 'glass-pill text-slate-300 hover:text-[var(--ink)]'
          }`}
        >
          <BarChart3 className="w-3.5 h-3.5 text-emerald-400" /> Evaluation Benchmarks
        </button>
      </div>

      {/* Subtab 1: Document Inventory */}
      {activeSubTab === 'documents' && (
        <div className="space-y-4">
          {documentError && <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs" role="alert">{documentError}</div>}
          <div className="p-4 rounded-2xl glass-panel flex items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-9 h-9 rounded-lg bg-emerald-600/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center shrink-0 shadow-sm">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-[var(--ink)] text-sm">Curriculum Source Registry</h3>
                <p className="text-xs text-slate-400">
                  {documents.length} official regulation documents indexed · {documents.reduce((sum, doc) => sum + doc.pages, 0).toLocaleString()} cataloged pages
                </p>
              </div>
            </div>
            <span className="px-2.5 py-1 rounded-md glass-pill text-emerald-400 text-xs font-semibold">
              {documentError ? 'Unavailable' : 'Live Knowledge Registry'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 rounded-2xl glass-card space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                    {doc.id}
                  </span>
                  <span className="text-[11px] text-slate-400 font-medium">{doc.pages} Pages</span>
                </div>
                <h3 className="font-semibold text-slate-200 text-sm">{doc.name} Department</h3>
                <p className="text-xs text-slate-400 leading-relaxed truncate" title={doc.file}>{doc.file}</p>
                <div className="pt-2 border-t border-[var(--ink)]/10 flex items-center justify-between text-xs text-slate-400">
                  <span>PDF Document</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <Check className="w-3 h-3" /> {doc.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Subtab 2: Issues and Conflicts */}
      {activeSubTab === 'issues' && (
        <div className="space-y-4">
          <div className="p-4 rounded-2xl glass-panel flex items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-[var(--ink)] text-sm">Discrepancy Audit Log</h3>
              <p className="text-xs text-slate-400">
                Disagreements identified between departmental PDFs (e.g., cross-listed course title variations, credit inconsistencies).
              </p>
            </div>
            <button
              aria-label="Refresh extraction issues"
              onClick={loadData}
              className="p-2 rounded-lg glass-pill text-slate-400 hover:text-[var(--ink)] transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {_loading ? (
            <div className="p-8 text-center text-slate-400 text-xs">Loading extraction records…</div>
          ) : loadError ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs" role="alert">{loadError}</div>
          ) : issues.length === 0 ? (
            <div className="p-12 text-center rounded-2xl glass-panel text-slate-400">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-500" />
              <h3 className="text-sm font-semibold text-slate-300">No Discrepancies Found</h3>
              <p className="text-xs text-slate-500 mt-1">All extracted courses and regulations match official records.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {issues.map((issue) => (
                <div
                  key={issue.id}
                  className="p-4 rounded-2xl glass-card space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded glass-pill text-blue-400">
                        {issue.course_code || 'GLOBAL'}
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded glass-pill text-slate-300">
                        {issue.issue_type}
                      </span>
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                        issue.severity === 'high' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {issue.severity}
                      </span>
                    </div>

                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-md ${
                      issue.status === 'resolved'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      Status: {issue.status}
                    </span>
                  </div>

                  <div className="p-3 rounded-lg glass-input text-xs font-mono text-slate-300 overflow-x-auto">
                    {typeof issue.details === 'object' ? JSON.stringify(issue.details, null, 2) : issue.details}
                  </div>

                  {issue.status === 'pending' && user?.role === 'admin' && (
                    <div className="flex items-center justify-end gap-2 pt-2 border-t border-[var(--ink)]/10">
                      {resolvingId === issue.id ? (
                        <div className="flex items-center gap-2 w-full sm:w-auto">
                          <input
                            type="text"
                            aria-label="Resolution notes"
                            placeholder="Resolution notes..."
                            value={resolutionNotes}
                            onChange={(e) => setResolutionNotes(e.target.value)}
                            className="glass-input text-xs text-slate-100 rounded-lg px-2.5 py-1.5 focus:outline-none"
                          />
                          <button
                            onClick={() => handleResolveIssue(issue.id, 'resolved')}
                            className="px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-[var(--ink)] text-xs font-semibold"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => handleResolveIssue(issue.id, 'suppressed')}
                            className="px-2.5 py-1.5 rounded-lg glass-pill text-slate-300 text-xs font-semibold"
                          >
                            Suppress
                          </button>
                          <button
                            aria-label="Cancel resolution"
                            onClick={() => setResolvingId(null)}
                            className="p-1.5 text-slate-500 hover:text-slate-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setResolvingId(issue.id)}
                          className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-[var(--paper)] text-xs font-semibold transition-all shadow-md shadow-blue-600/30"
                        >
                          Resolve Conflict
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Subtab 3: Metrics */}
      {activeSubTab === 'metrics' && (
        <div className="space-y-6">
          {_loading ? (
            <div className="p-8 text-center text-slate-400 text-xs">Loading evaluation results…</div>
          ) : !metrics ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs" role="alert">
              Evaluation results are unavailable.
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl glass-panel">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Intent Macro F1</span>
                  <div className="text-2xl font-bold text-[var(--ink)] mt-1">{percentage(metrics.intent_classification?.test_macro_f1)}</div>
                  <p className="text-xs text-slate-400 mt-1">Across evaluated intent classes</p>
                </div>
                <div className="p-4 rounded-2xl glass-panel">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Top-1 Accuracy</span>
                  <div className="text-2xl font-bold text-[var(--ink)] mt-1">{percentage(metrics.intent_classification?.test_top1_accuracy)}</div>
                  <p className="text-xs text-slate-400 mt-1">{metrics.intent_classification?.test_samples ?? '—'} test queries</p>
                </div>
                <div className="p-4 rounded-2xl glass-panel">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Retrieval Recall @ 5</span>
                  <div className="text-2xl font-bold text-[var(--ink)] mt-1">{percentage(metrics.retrieval_benchmarks?.measured_recall_at_5)}</div>
                  <p className="text-xs text-slate-400 mt-1">Top-5 handbook retrieval</p>
                </div>
                <div className="p-4 rounded-2xl glass-panel">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Exact Fact Accuracy</span>
                  <div className="text-2xl font-bold text-[var(--ink)] mt-1">{percentage(metrics.retrieval_benchmarks?.exact_fact_accuracy)}</div>
                  <p className="text-xs text-slate-400 mt-1">Structured academic answers</p>
                </div>
              </div>

              <div className="p-5 rounded-2xl glass-panel space-y-3">
                <h3 className="text-sm font-bold text-[var(--ink)]">Evaluation Context & Methodology</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-[var(--ink)]/10 text-xs">
                  <div>
                    <span className="text-slate-400 block">Training Samples:</span>
                    <strong className="text-slate-200 mt-0.5 block">{metrics.intent_classification?.trained_samples ?? 'Unavailable'}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Intent Classes:</span>
                    <strong className="text-slate-200 mt-0.5 block">{metrics.intent_classification?.num_classes ?? 'Unavailable'}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Retrieval Engine:</span>
                    <strong className="text-slate-200 mt-0.5 block">{metrics.retrieval_benchmarks?.retriever ?? 'Unavailable'}</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Mean Reciprocal Rank:</span>
                    <strong className="text-slate-200 mt-0.5 block">{metrics.retrieval_benchmarks?.measured_mrr ?? 'Unavailable'}</strong>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

