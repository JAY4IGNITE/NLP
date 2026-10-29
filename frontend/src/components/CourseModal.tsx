import React, { useEffect, useState } from 'react';
import { X, Award, Layers, Clock, FileText, BookOpen, Bookmark, MessageSquare } from 'lucide-react';
import type { CourseDetail } from '../types';
import { ModalFrame } from './ui/ModalFrame';
import { api } from '../api';

interface CourseModalProps {
  courseId: number | null;
  onClose: () => void;
  onViewSource: (docId: string, page: number, title: string, dept: string) => void;
  onAskAI?: (prompt: string) => void;
}

export const CourseModal: React.FC<CourseModalProps> = ({ courseId, onClose, onViewSource, onAskAI }) => {
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'units' | 'outcomes' | 'books'>('units');
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    if (!courseId) return;
    setLoading(true);
    setCourse(null);
    setLoadError('');
    api.getCourseDetail(courseId)
      .then(setCourse)
      .catch(() => setLoadError('The course details could not be loaded. Close and reopen this course to retry.'))
      .finally(() => setLoading(false));
  }, [courseId]);

  if (!courseId) return null;

  return (
    <ModalFrame onClose={onClose} label="Course details">
      {/* Header */}
      <div className="px-6 py-5 border-b border-[var(--line)] bg-[var(--paper)] flex items-start justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-[var(--surface-soft)] text-zinc-200 border border-[var(--line)]">
              {course?.code}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[var(--surface)] border border-[var(--line)] text-zinc-300">
              {course?.credits.toFixed(1)} Credits
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[var(--surface)] border border-[var(--line)] text-zinc-400">
              {course?.category} ({course?.level})
            </span>
          </div>

          <h2 className="text-xl font-bold text-[var(--ink)] font-heading">
            {loading ? 'Loading course…' : course?.title || 'Course Details'}
          </h2>

          <div className="flex flex-wrap items-center gap-3.5 text-xs text-zinc-400 pt-1">
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-zinc-500" />
              L: <strong className="text-zinc-200">{course?.lecture_hours}</strong> | T: <strong className="text-zinc-200">{course?.tutorial_hours}</strong> | P: <strong className="text-zinc-200">{course?.practical_hours}</strong> (Total: {course?.total_hours} hrs)
            </span>

            {course?.source_document_id && course?.source_page && (
              <button
                onClick={() => onViewSource(course.source_document_id!, course.source_page!, course.title, course.department_code || '')}
                className="flex items-center gap-1 text-zinc-300 hover:text-[var(--ink)] font-medium transition-colors cursor-pointer"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Source Page {course.source_page}</span>
              </button>
            )}

            {onAskAI && course && (
              <button
                onClick={() => {
                  onClose();
                  onAskAI(`Explain the course units and textbooks for ${course.title} (${course.code})`);
                }}
                className="flex items-center gap-1 text-zinc-300 hover:text-[var(--ink)] font-medium transition-colors cursor-pointer"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Inquire About Course</span>
              </button>
            )}
          </div>
        </div>

        <button
          aria-label="Close course details"
          onClick={onClose}
          className="p-1.5 text-zinc-400 hover:text-[var(--ink)] bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] rounded-lg transition-colors shrink-0 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-[var(--line)] px-6 bg-[var(--paper)]">
        <button
          aria-pressed={activeTab === 'units'}
          onClick={() => setActiveTab('units')}
          className={`flex items-center gap-2 py-3 px-4 border-b-2 text-xs font-semibold transition-colors cursor-pointer ${
            activeTab === 'units'
              ? 'border-[var(--ink)] text-[var(--ink)]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Layers className="w-3.5 h-3.5" /> Syllabus Units ({course?.units?.length || 0})
        </button>
        <button
          aria-pressed={activeTab === 'outcomes'}
          onClick={() => setActiveTab('outcomes')}
          className={`flex items-center gap-2 py-3 px-4 border-b-2 text-xs font-semibold transition-colors cursor-pointer ${
            activeTab === 'outcomes'
              ? 'border-[var(--ink)] text-[var(--ink)]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <Award className="w-3.5 h-3.5" /> Course Outcomes ({course?.outcomes?.length || 0})
        </button>
        <button
          aria-pressed={activeTab === 'books'}
          onClick={() => setActiveTab('books')}
          className={`flex items-center gap-2 py-3 px-4 border-b-2 text-xs font-semibold transition-colors cursor-pointer ${
            activeTab === 'books'
              ? 'border-[var(--ink)] text-[var(--ink)]'
              : 'border-transparent text-zinc-400 hover:text-zinc-200'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" /> Prescribed Textbooks ({course?.textbooks?.length || 0})
        </button>
      </div>

      {/* Tab Body */}
      <div tabIndex={0} aria-label="Course detail content" className="flex-1 overflow-y-auto p-6 space-y-4 bg-[var(--paper)]">
        {loadError ? (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs" role="alert">
            {loadError}
          </div>
        ) : loading ? (
          <div className="flex justify-center py-12 text-zinc-400 text-xs font-medium">
            Loading verified academic syllabus…
          </div>
        ) : (
          <>
            {activeTab === 'units' && (
              <div className="space-y-3.5">
                {course?.units?.map((unit) => (
                  <div key={unit.unit_number} className="p-4 rounded-xl bg-[var(--surface)] border border-[var(--line)] space-y-2 shadow-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-[var(--surface-soft)] text-zinc-200 border border-[var(--line)] font-mono">
                        {unit.unit_roman}
                      </span>
                      {unit.title && (
                        <h4 className="text-xs font-bold text-[var(--ink)] flex-1 ml-2">{unit.title}</h4>
                      )}
                    </div>
                    <p className="text-xs text-zinc-300 leading-relaxed">{unit.content}</p>
                    {unit.practice_content && (
                      <div className="mt-2.5 p-2.5 rounded-lg bg-[var(--paper)] border border-[var(--line)] text-xs">
                        <span className="font-semibold text-emerald-400">Practice / Laboratory Component: </span>
                        <span className="text-zinc-300">{unit.practice_content}</span>
                      </div>
                    )}
                  </div>
                ))}
                {course?.units?.length === 0 && (
                  <div className="text-center py-8 text-zinc-400 text-xs">
                    Syllabus details available in full curriculum documentation.
                  </div>
                )}
              </div>
            )}

            {activeTab === 'outcomes' && (
              <div className="space-y-2.5">
                {course?.outcomes?.map((co) => (
                  <div key={co.outcome_code} className="flex gap-3 p-3.5 rounded-xl bg-[var(--surface)] border border-[var(--line)] shadow-xs">
                    <span className="text-[11px] font-mono font-bold px-2 py-0.5 h-fit rounded bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300">
                      {co.outcome_code}
                    </span>
                    <p className="text-xs text-zinc-200 leading-relaxed">{co.description}</p>
                  </div>
                ))}
                {course?.outcomes?.length === 0 && (
                  <div className="text-center py-8 text-zinc-400 text-xs">
                    Course outcomes are specified in the official department syllabus.
                  </div>
                )}
              </div>
            )}

            {activeTab === 'books' && (
              <div className="space-y-2.5">
                {!course?.textbooks?.length && (
                  <p className="text-zinc-400 text-xs text-center py-8">
                    No textbook references supplied in the digitized index. Consult the source handbook page.
                  </p>
                )}
                {course?.textbooks?.map((tb, idx) => (
                  <div key={idx} className="flex gap-3 p-3.5 rounded-xl bg-[var(--surface)] border border-[var(--line)] shadow-xs">
                    <Bookmark className="w-4 h-4 text-zinc-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 block mb-0.5 font-mono">
                        {tb.book_type}
                      </span>
                      <p className="text-xs text-zinc-200 font-medium">{tb.title}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </ModalFrame>
  );
};

