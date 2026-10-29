import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowUp, ArrowDown, BookOpen, CalendarCheck, ClipboardList,
  GraduationCap, Search, ShieldCheck, Square, Check, Copy, RotateCcw,
  ChevronDown, Volume2, VolumeX, ThumbsUp, ThumbsDown,
  Download
} from 'lucide-react';
import { api } from '../api';
import { BrandMark } from './ui/BrandMark';
import type { ChatMessageItem } from '../types';

interface ChatViewProps {
  isActive?: boolean;
  onViewSource?: (docId: string, page: number, title: string, dept: string) => void;
  initialQuery?: string;
  onClearInitialQuery?: () => void;
}

const DEPARTMENTS = [
  { code: 'ALL', name: 'All Departments', short: 'All Disciplines' },
  { code: 'CSE', name: 'Computer Science & Engineering', short: 'CSE' },
  { code: 'IT', name: 'Information Technology', short: 'IT' },
  { code: 'ECE', name: 'Electronics & Communication', short: 'ECE' },
  { code: 'EEE', name: 'Electrical & Electronics', short: 'EEE' },
  { code: 'CE', name: 'Civil Engineering', short: 'Civil' },
  { code: 'MIN', name: 'Mining Engineering', short: 'Mining' },
  { code: 'PT', name: 'Petroleum Technology', short: 'Petroleum' },
  { code: 'CSE-DS', name: 'CSE - Data Science', short: 'CSE-DS' },
];

const TOPIC_SUGGESTIONS = [
  {
    id: 'attendance',
    title: 'Attendance requirements',
    prompt: 'What is the minimum attendance requirement and condonation rule under R24?',
    icon: CalendarCheck,
    colorClass: 'topic-attendance'
  },
  {
    id: 'courses',
    title: 'Courses & curriculum',
    prompt: 'What courses and credits are scheduled in CSE Semester 3?',
    icon: BookOpen,
    colorClass: 'topic-courses'
  },
  {
    id: 'exams',
    title: 'Exams & assessment',
    prompt: 'What is the examination assessment and grading pattern under Regulation 2024?',
    icon: ClipboardList,
    colorClass: 'topic-exams'
  },
  {
    id: 'grading',
    title: 'Grades & passing marks',
    prompt: 'How are SGPA and CGPA calculated under Aditya University Regulation 2024?',
    icon: GraduationCap,
    colorClass: 'topic-grading'
  }
];

const stripSourceCitations = (text: string): string => {
  if (!text) return '';
  return text
    .replace(/\n*\*\*Source Citation:\*\*[\s\S]*$/gi, '')
    .replace(/\n*Source Citation:[\s\S]*$/gi, '')
    .replace(/\n*\[Doc:\s*[^\]]+\]/gi, '')
    .replace(/\n*Citations:[\s\S]*$/gi, '')
    .trim();
};

export const ChatView: React.FC<ChatViewProps> = ({
  isActive = true,
  onViewSource: _onViewSource,
  initialQuery,
  onClearInitialQuery
}) => {
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [input, setInput] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [showJump, setShowJump] = useState(false);
  const [isDeptDropdownOpen, setIsDeptDropdownOpen] = useState(false);
  const [speakingIndex, setSpeakingIndex] = useState<number | null>(null);
  const [copyStatusMap, setCopyStatusMap] = useState<Record<number, string>>({});
  const [feedbackStatus, setFeedbackStatus] = useState('');

  const scrollRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const deptDropdownRef = useRef<HTMLDivElement>(null);
  const startTimeRef = useRef<number>(0);
  const abortControllerRef = useRef<AbortController | null>(null);

  const empty = messages.length === 0;

  // Auto-scroll to end when messages update and user is not looking up
  useEffect(() => {
    if (!showJump) {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages.length, loading, showJump]);

  // Dynamic textarea sizing up to 176px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 176)}px`;
    }
  }, [input]);

  // Close department dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (deptDropdownRef.current && !deptDropdownRef.current.contains(e.target as Node)) {
        setIsDeptDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle initial query from another tab
  useEffect(() => {
    if (initialQuery && isActive) {
      handleSend(initialQuery);
      if (onClearInitialQuery) onClearInitialQuery();
    }
  }, [initialQuery, isActive]);

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    setInput('');
    setShowJump(false);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    // Append user message
    const userMsg: ChatMessageItem = {
      role: 'user',
      content: textToSend
    };
    setMessages(prev => [...prev, userMsg]);

    startTimeRef.current = Date.now();
    setLoading(true);

    try {
      const dept = selectedDept === 'ALL' ? undefined : selectedDept;
      const resp = await api.sendChat(textToSend, sessionId || undefined, dept);

      if (resp.session_id) {
        setSessionId(resp.session_id);
      }

      const duration = Math.max(0.6, (Date.now() - startTimeRef.current) / 1000);

      const asstMsg: ChatMessageItem = {
        role: 'assistant',
        content: stripSourceCitations(resp.answer) || 'No response returned from the campus knowledge base.',
        is_grounded: resp.is_grounded === true,
        intent: resp.intent,
        domain: resp.domain,
        confidence: resp.confidence,
        thinkingDuration: Number(duration.toFixed(1)),
        citations: resp.citations || []
      };

      setMessages(prev => [...prev, asstMsg]);
    } catch (err: any) {
      console.error('Chat request failed:', err);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Unable to connect to the campus curriculum database. Please ensure the backend server is running and retry.',
          is_grounded: false,
          error: true,
          thinkingDuration: 0.4
        }
      ]);
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleSpeech = (text: string, index: number) => {
    if (!('speechSynthesis' in window)) return;
    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanText = stripSourceCitations(text).replace(/[*_#`[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);
    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  };

  const copyAnswer = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(stripSourceCitations(text));
      setCopyStatusMap(prev => ({ ...prev, [index]: 'Copied' }));
      setTimeout(() => {
        setCopyStatusMap(prev => ({ ...prev, [index]: '' }));
      }, 2000);
    } catch {
      setCopyStatusMap(prev => ({ ...prev, [index]: 'Copy unavailable' }));
    }
  };

  const handleFeedback = async (rating: number) => {
    setFeedbackStatus('Recording feedback…');
    try {
      const feedbackResult = await api.submitFeedback(sessionId, rating);
      setFeedbackStatus(feedbackResult?.detail ? 'Feedback could not be recorded.' : 'Thank you for your feedback.');
      setTimeout(() => setFeedbackStatus(''), 2500);
    } catch {
      setFeedbackStatus('Feedback could not be recorded.');
      setTimeout(() => setFeedbackStatus(''), 2500);
    }
  };

  const exportConversation = () => {
    const transcript = messages.map(m => `### ${m.role === 'user' ? 'Student' : 'CampusAI'}\n${stripSourceCitations(m.content)}\n`).join('\n---\n\n');
    const blob = new Blob([`# CampusAI Academic Helpdesk Session\nDate: ${new Date().toLocaleString()}\n\n${transcript}`], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CampusAI_Session_${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const resetConversation = () => {
    setMessages([]);
    setSessionId('');
    setInput('');
    setFeedbackStatus('');
    if (speakingIndex !== null) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
    }
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.focus();
    }
  };

  // Helper for inline markdown formatting (**bold**, `code`)
  const renderInline = (text: string) => {
    return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx} className="font-semibold text-[var(--text)]">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={pIdx} className="px-1.5 py-0.5 rounded bg-[var(--surface-muted)] text-[var(--accent-text)] font-mono text-xs border border-[var(--border)]">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  // Clean formatted content renderer supporting paragraphs, lists, and markdown tables
  const renderFormattedContent = (content: string) => {
    const clean = stripSourceCitations(content);
    const blocks = clean.split('\n\n');

    return blocks.map((block, bIdx) => {
      const lines = block.trim().split('\n');

      // 1. Markdown Table Check
      if (lines.length >= 2 && lines[0].includes('|') && lines[1].includes('|') && lines[1].includes('-')) {
        const headerCells = lines[0].split('|').map(c => c.trim()).filter(Boolean);
        const rowLines = lines.slice(2).filter(l => l.includes('|'));

        return (
          <div key={bIdx} className="overflow-x-auto my-3 rounded-xl border border-[var(--border)] bg-[var(--surface-raised)]">
            <table className="w-full text-xs text-left text-[var(--text)] border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)] bg-[var(--surface-muted)] text-[var(--text)] font-semibold">
                  {headerCells.map((h, hIdx) => (
                    <th key={hIdx} className="px-3.5 py-2.5">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)]">
                {rowLines.map((row, rIdx) => {
                  const cells = row.split('|').map(c => c.trim()).filter(Boolean);
                  return (
                    <tr key={rIdx} className="hover:bg-[var(--surface-hover)] transition-colors">
                      {cells.map((cell, cIdx) => (
                        <td key={cIdx} className="px-3.5 py-2 font-mono text-[12px]">{cell}</td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
      }

      // 2. Bullet / Numbered List Check
      if (lines.length > 0 && lines.every(l => l.trim().startsWith('- ') || l.trim().startsWith('* ') || /^\d+\.\s/.test(l.trim()))) {
        return (
          <ul key={bIdx} className="space-y-1.5 my-2 pl-1 text-[14px] text-[var(--text)]">
            {lines.map((l, lIdx) => {
              const isBullet = l.trim().startsWith('- ') || l.trim().startsWith('* ');
              const text = isBullet ? l.trim().replace(/^[-*]\s+/, '') : l.trim().replace(/^\d+\.\s+/, '');
              return (
                <li key={lIdx} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] mt-2 shrink-0" />
                  <span className="leading-relaxed">{renderInline(text)}</span>
                </li>
              );
            })}
          </ul>
        );
      }

      // 3. Headings
      if (block.startsWith('### ')) {
        return (
          <h3 key={bIdx} className="text-sm font-semibold text-[var(--text)] mt-3 mb-1">
            {renderInline(block.replace('### ', ''))}
          </h3>
        );
      }
      if (block.startsWith('## ')) {
        return (
          <h2 key={bIdx} className="text-base font-semibold text-[var(--text)] mt-3.5 mb-1.5">
            {renderInline(block.replace('## ', ''))}
          </h2>
        );
      }

      // 4. Regular Paragraph
      return (
        <p key={bIdx} className="leading-relaxed text-[var(--text)]">
          {renderInline(block)}
        </p>
      );
    });
  };

  const composer = (
    <div className="composer-area">
      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <label className="sr-only" htmlFor="question">Your campus question</label>
        <textarea
          ref={textareaRef}
          id="question"
          rows={1}
          maxLength={2000}
          placeholder="Ask about courses, exams, campus rules…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <div className="composer-toolbar">
          <div className="composer-context">
            <BookOpen size={15} />
            <span>Campus knowledge</span>
            <span className="context-separator">·</span>
            <span>B.Tech Regulation 2024</span>
            <span className="context-separator">·</span>
            
            {/* Department filter badge with clean dropdown */}
            <div className="relative inline-block" ref={deptDropdownRef}>
              <button
                type="button"
                onClick={() => setIsDeptDropdownOpen(prev => !prev)}
                className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[var(--surface-muted)] hover:bg-[var(--surface-hover)] border border-[var(--border)] text-[10.5px] font-medium text-[var(--text)] transition-colors cursor-pointer"
                title="Filter by department"
              >
                <span>{selectedDept === 'ALL' ? 'All Disciplines' : selectedDept}</span>
                <ChevronDown size={11} className="text-[var(--text-muted)]" />
              </button>
              {isDeptDropdownOpen && (
                <div className="absolute bottom-full left-0 mb-2 w-56 rounded-xl bg-[var(--surface-raised)] border border-[var(--border-strong)] p-1.5 shadow-xl z-50 text-left">
                  <div className="text-[9.5px] uppercase tracking-wider font-semibold text-[var(--text-muted)] px-2 py-1">
                    Filter by Discipline
                  </div>
                  <div className="max-h-48 overflow-y-auto space-y-0.5">
                    {DEPARTMENTS.map((dept) => (
                      <button
                        key={dept.code}
                        type="button"
                        onClick={() => {
                          setSelectedDept(dept.code);
                          setIsDeptDropdownOpen(false);
                        }}
                        className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs flex items-center justify-between transition-colors cursor-pointer ${
                          selectedDept === dept.code
                            ? 'bg-[var(--accent-soft)] text-[var(--accent)] font-semibold'
                            : 'text-[var(--text-secondary)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)]'
                        }`}
                      >
                        <span className="truncate">{dept.code} · {dept.name}</span>
                        {selectedDept === dept.code && <Check size={12} className="text-[var(--accent)] shrink-0" />}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="composer-actions">
            {input.length > 1800 && (
              <span className="character-count">{input.length}/2000</span>
            )}
            {loading ? (
              <button
                type="button"
                className="send-button stop-button"
                onClick={handleStop}
                aria-label="Stop request"
                title="Stop request"
              >
                <Square size={14} fill="currentColor" />
              </button>
            ) : (
              <button
                type="submit"
                className="send-button"
                disabled={!input.trim()}
                aria-label="Send question"
                title="Send question"
              >
                <ArrowUp size={18} />
              </button>
            )}
          </div>
        </div>
      </form>
      <p className="composer-caption">
        Ask one complete question at a time. <span className="keyboard-hint"><kbd>Shift</kbd> + <kbd>Enter</kbd> for a new line.</span>
      </p>
    </div>
  );

  return (
    <div className="flex flex-1 h-full w-full overflow-hidden bg-[var(--surface)] text-[var(--text)]">
      {/* Middle Main Workspace */}
      <section className={`chat-workspace ${empty ? 'is-empty' : 'has-conversation'}`}>
        {/* Scroll Container */}
        <div
          className="chat-scroll"
          ref={scrollRef}
          onScroll={() => {
            const el = scrollRef.current;
            if (el) {
              setShowJump(el.scrollHeight - el.scrollTop - el.clientHeight > 160);
            }
          }}
        >
          {empty ? (
            /* Empty State Hero - Exact match to NLP-cornerstone */
            <div className="welcome-content">
              <div className="welcome-brand">
                <BrandMark />
              </div>
              <div className="welcome-eyebrow">YOUR CAMPUS, CLARIFIED</div>
              <h1>
                A little less searching.<br />
                <span>A lot more clarity.</span>
              </h1>
              <p className="welcome-description">
                From your first lecture to your final exam.<br className="mobile-linebreak" /> Find answers in your campus knowledge base.
              </p>

              {/* Fast Department Selector Chips */}
              <div className="flex flex-wrap items-center justify-center gap-1.5 mb-5">
                {DEPARTMENTS.map((dept) => {
                  const isSelected = selectedDept === dept.code;
                  return (
                    <button
                      key={dept.code}
                      type="button"
                      onClick={() => setSelectedDept(dept.code)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${
                        isSelected
                          ? 'bg-gradient-to-r from-[#2997ff] to-[#0071e3] text-white font-semibold shadow-md shadow-blue-500/25 scale-[1.03]'
                          : 'bg-[var(--surface-raised)] hover:bg-[var(--surface-hover)] hover:border-[var(--accent)]/40 hover:scale-[1.02] text-[var(--text-secondary)] hover:text-[var(--text)] border border-[var(--border)]'
                      }`}
                    >
                      {dept.short}
                    </button>
                  );
                })}
              </div>

              {composer}

              <div className="suggestions-heading">
                <span>A good place to start</span>
                <span className="text-[11px] text-[var(--text-muted)]">Verified against AR24</span>
              </div>

              <div className="suggestions-grid">
                {TOPIC_SUGGESTIONS.map((topic) => {
                  const Icon = topic.icon;
                  return (
                    <button
                      key={topic.id}
                      type="button"
                      className="suggestion-card"
                      onClick={() => handleSend(topic.prompt)}
                    >
                      <span className={`suggestion-icon ${topic.colorClass}`}>
                        <Icon size={19} strokeWidth={1.7} />
                      </span>
                      <span className="suggestion-copy">
                        <strong>{topic.title}</strong>
                        <span>{topic.prompt}</span>
                      </span>
                      <ArrowUp size={16} className="suggestion-arrow" />
                    </button>
                  );
                })}
              </div>

              <div className="welcome-trust">
                <ShieldCheck size={15} />
                <span>Grounded in the collection. Sources included when available.</span>
              </div>
            </div>
          ) : (
            /* Active Message Stream */
            <div
              className="message-list"
              role="log"
              aria-label="Conversation"
              aria-live="polite"
              aria-relevant="additions text"
            >
              {messages.map((message, idx) => {
                const isUser = message.role === 'user';
                const copyStatus = copyStatusMap[idx] || '';

                if (isUser) {
                  return (
                    <article key={idx} className="user-message" aria-label="Your question">
                      <p>{message.content}</p>
                    </article>
                  );
                }

                const topic = message.intent?.replace(/_/g, ' ');

                return (
                  <article
                    key={idx}
                    className={`assistant-message ${message.error ? 'is-error' : ''}`}
                    aria-label={message.error ? 'Request error' : 'CampusAI answer'}
                  >
                    <div className="assistant-avatar">
                      <BrandMark />
                    </div>
                    <div className="assistant-content">
                      <div className="message-byline">
                        <strong>CampusAI</strong>
                        <span>Campus assistant · Aditya University</span>
                      </div>

                      <div className="answer-text">
                        {renderFormattedContent(message.content)}
                      </div>

                      {/* Details dropdown matching NLP-cornerstone */}
                      {!message.error && message.intent && (
                        <details className="answer-details">
                          <summary>
                            <ChevronDown size={14} />
                            <span>How this was matched</span>
                          </summary>
                          <div className="match-details">
                            <dl>
                              <div>
                                <dt>Detected topic</dt>
                                <dd>{topic}</dd>
                              </div>
                              {Number.isFinite(message.confidence) && (
                                <div>
                                  <dt>Intent confidence</dt>
                                  <dd>{Math.round((message.confidence || 0) * 100)}%</dd>
                                </div>
                              )}
                              <div>
                                <dt>Regulation version</dt>
                                <dd>Aditya University R24 (v3.0)</dd>
                              </div>
                            </dl>
                            <p>Confidence describes the topic match, grounded directly in verified curriculum records.</p>
                          </div>
                        </details>
                      )}

                      {/* Action bar */}
                      <div className="message-actions">
                        <button
                          className="icon-button"
                          onClick={() => copyAnswer(message.content, idx)}
                          title="Copy answer"
                          aria-label="Copy answer"
                        >
                          {copyStatus === 'Copied' ? <Check size={15} /> : <Copy size={15} />}
                        </button>
                        <button
                          className="icon-button"
                          onClick={() => handleSpeech(message.content, idx)}
                          title={speakingIndex === idx ? "Stop audio" : "Read aloud"}
                          aria-label={speakingIndex === idx ? "Stop audio" : "Read aloud"}
                        >
                          {speakingIndex === idx ? <VolumeX size={15} /> : <Volume2 size={15} />}
                        </button>
                        <button
                          className="icon-button"
                          onClick={() => handleFeedback(5)}
                          title="Helpful"
                          aria-label="Helpful"
                        >
                          <ThumbsUp size={14} />
                        </button>
                        <button
                          className="icon-button"
                          onClick={() => handleFeedback(1)}
                          title="Needs improvement"
                          aria-label="Needs improvement"
                        >
                          <ThumbsDown size={14} />
                        </button>
                        {copyStatus && <span className="copy-status" role="status">{copyStatus}</span>}
                      </div>
                    </div>
                  </article>
                );
              })}

              {loading && (
                <div className="thinking-message" role="status">
                  <div className="assistant-avatar">
                    <BrandMark state="thinking" />
                  </div>
                  <div>
                    <strong>Looking into it</strong>
                    <span>
                      <Search size={13} />
                      Matching your question with campus sources
                      <span className="loading-dots" aria-hidden="true"><i /><i /><i /></span>
                    </span>
                  </div>
                </div>
              )}

              <div ref={endRef} />
            </div>
          )}
        </div>

        {/* Floating Composer Dock when conversation is active */}
        {!empty && (
          <div className="chat-dock">
            <div className="flex items-center justify-between mb-2 px-1">
              {showJump ? (
                <button
                  className="jump-button"
                  onClick={() => {
                    setShowJump(false);
                    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
                  }}
                >
                  <ArrowDown size={15} />
                  <span>Latest message</span>
                </button>
              ) : <div />}

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={exportConversation}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-all cursor-pointer"
                  title="Export chat history"
                >
                  <Download size={12} />
                  <span>Export</span>
                </button>
                <button
                  type="button"
                  onClick={resetConversation}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)] border border-[var(--border)] transition-all cursor-pointer"
                  title="Start a new conversation"
                >
                  <RotateCcw size={12} />
                  <span>New Query</span>
                </button>
              </div>
            </div>
            {feedbackStatus && (
              <p className="text-xs text-center text-[var(--accent)] font-medium mb-1.5" role="status">
                {feedbackStatus}
              </p>
            )}
            {composer}
          </div>
        )}
      </section>
    </div>
  );
};

export default ChatView;
