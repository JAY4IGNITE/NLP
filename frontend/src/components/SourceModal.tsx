import React, { useState } from 'react';
import { X, ExternalLink, FileText, RefreshCw, ZoomIn } from 'lucide-react';
import { api } from '../api';
import { ModalFrame } from './ui/ModalFrame';

interface SourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  docId: string;
  pageNum: number;
  title: string;
  department: string;
}

export const SourceModal: React.FC<SourceModalProps> = ({
  isOpen, onClose, docId, pageNum, title, department
}) => {
  const [imageStatus, setImageStatus] = useState<'loading' | 'loaded' | 'error'>('loading');
  const [fitMode, setFitMode] = useState<'fit-page' | 'fit-width' | 'actual-size'>('fit-page');
  const [retryImage, setRetryImage] = useState(0);

  if (!isOpen) return null;

  const imageUrl = api.getSourcePageImageUrl(docId, pageNum);

  return (
    <ModalFrame onClose={onClose} label="Source document viewer" className="source-dialog">
      {/* Header */}
      <div className="px-6 py-4 flex items-center justify-between border-b border-[var(--ink)]/10 bg-slate-900/60 backdrop-blur-xl gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-xl bg-blue-600/15 border border-blue-500/25 text-blue-400 flex items-center justify-center shrink-0 shadow-sm">
            <FileText className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold text-blue-400 uppercase tracking-wider">
                Original Official Source · Page {pageNum}
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded glass-pill text-slate-300">
                {docId}
              </span>
            </div>
            <h3 className="text-sm font-bold text-[var(--ink)] truncate mt-0.5">{title}</h3>
            <p className="text-[11px] text-slate-400">{department} Department · Academic Regulation 2024</p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <a
            href={imageUrl}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open raw handbook page in new tab"
            title="Open raw handbook page in new tab"
            className="p-2 rounded-lg glass-pill text-slate-300 hover:text-[var(--ink)] transition-colors"
          >
            <ExternalLink size={16} />
          </a>
          <button
            onClick={onClose}
            aria-label="Close source viewer"
            className="p-2 rounded-lg glass-pill text-slate-300 hover:text-[var(--ink)] transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="px-6 py-2.5 bg-slate-950/40 backdrop-blur-md border-b border-[var(--ink)]/10 flex items-center justify-between gap-4 text-xs" aria-label="Document view controls">
        <span className="text-slate-400 font-medium hidden sm:inline flex items-center gap-1.5">
          <ZoomIn className="w-3.5 h-3.5 text-blue-400" /> Page Zoom:
        </span>
        <div className="flex items-center gap-1 p-0.5 rounded-lg glass-pill">
          <button
            aria-pressed={fitMode === 'fit-page'}
            onClick={() => setFitMode('fit-page')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              fitMode === 'fit-page'
                ? 'bg-blue-600 text-[var(--paper)] shadow-sm ring-1 ring-white/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Fit Page
          </button>
          <button
            aria-pressed={fitMode === 'fit-width'}
            onClick={() => setFitMode('fit-width')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              fitMode === 'fit-width'
                ? 'bg-blue-600 text-[var(--paper)] shadow-sm ring-1 ring-white/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Fit Width
          </button>
          <button
            aria-pressed={fitMode === 'actual-size'}
            onClick={() => setFitMode('actual-size')}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              fitMode === 'actual-size'
                ? 'bg-blue-600 text-[var(--paper)] shadow-sm ring-1 ring-white/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Actual Size
          </button>
        </div>
      </div>

      {/* Viewport */}
      <div className="source-viewport flex-1 min-h-0 overflow-auto p-6 bg-slate-950 flex items-center justify-center">
        {imageStatus === 'loading' && (
          <div role="status" className="flex flex-col items-center gap-3 text-slate-400">
            <div className="w-7 h-7 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs">Loading verified curriculum handbook scan…</p>
          </div>
        )}
        {imageStatus === 'error' && (
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 text-center max-w-sm space-y-3" role="alert">
            <h4 className="text-sm font-semibold text-slate-200">This source page is currently unavailable</h4>
            <p className="text-xs text-slate-400">The document scan file could not be retrieved from the academic repository.</p>
            <button
              className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-[var(--paper)] text-xs font-semibold inline-flex items-center gap-1.5 transition-colors"
              onClick={() => { setImageStatus('loading'); setRetryImage(value => value + 1); }}
            >
              <RefreshCw size={13} /> Retry Document Page
            </button>
          </div>
        )}
        <img
          key={retryImage}
          src={imageUrl}
          alt={`${title}, ${department}, page ${pageNum}`}
          className={`source-image rounded shadow-2xl ${fitMode}`}
          hidden={imageStatus !== 'loaded'}
          onLoad={() => setImageStatus('loaded')}
          onError={() => setImageStatus('error')}
        />
      </div>
    </ModalFrame>
  );
};

