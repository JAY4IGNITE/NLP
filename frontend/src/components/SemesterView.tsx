import React, { useState, useEffect } from 'react';
import {
  Calendar, Layers, ExternalLink, Compass,
  BookOpen, MessageSquare
} from 'lucide-react';
import { api } from '../api';
import type { Department, SemesterData } from '../types';

interface SemesterViewProps {
  onViewSource: (docId: string, page: number) => void;
  onAskAI?: (prompt: string) => void;
}

export const SemesterView: React.FC<SemesterViewProps> = ({
  onViewSource,
  onAskAI
}) => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDept, setSelectedDept] = useState<string>('CSE');
  const [selectedSem, setSelectedSem] = useState<number>(1);
  const [semesterData, setSemesterData] = useState<SemesterData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    api.getDepartments().then(depts => {
      setDepartments(depts);
      if (depts.length > 0 && !selectedDept) {
        setSelectedDept(depts[0].code);
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedDept) return;
    setLoading(true);
    setLoadError('');
    api.getSemester(selectedDept, selectedSem)
      .then(data => {
        setSemesterData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoadError('This semester could not be loaded. Please select another department or semester to retry.');
        setSemesterData(null);
        setLoading(false);
      });
  }, [selectedDept, selectedSem]);

  const semesters = [
    { num: 1, roman: 'I', label: 'Sem I' },
    { num: 2, roman: 'II', label: 'Sem II' },
    { num: 3, roman: 'III', label: 'Sem III' },
    { num: 4, roman: 'IV', label: 'Sem IV' },
    { num: 5, roman: 'V', label: 'Sem V' },
    { num: 6, roman: 'VI', label: 'Sem VI' },
    { num: 7, roman: 'VII', label: 'Sem VII' },
    { num: 8, roman: 'VIII', label: 'Sem VIII' }
  ];

  // Category counts and course delivery breakdown
  const categoryCounts: { [cat: string]: number } = {};
  let theoryCount = 0;
  let practicalCount = 0;

  if (semesterData?.courses) {
    semesterData.courses.forEach(c => {
      const cat = c.category || 'Core';
      categoryCounts[cat] = (categoryCounts[cat] || 0) + (c.credits || 0);

      const isLab = (c.practical_hours && c.practical_hours > 0) || c.title.toLowerCase().includes('lab') || c.title.toLowerCase().includes('practice');
      if (isLab) {
        practicalCount++;
      } else {
        theoryCount++;
      }
    });
  }

  return (
    <div className="workspace-view view-enter space-y-6 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-[var(--line)]">
        <div>
          <div className="text-[11px] font-bold text-zinc-400 tracking-wider uppercase flex items-center gap-1.5 font-mono">
            <Calendar className="w-3.5 h-3.5" /> Academic Regulation 2024 (Version 3.0)
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--ink)] mt-1 font-heading">
            Your semester, at a glance
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-2xl">
            Sequential course progression, credit allocations, and category distribution across all 8 semesters.
          </p>
        </div>

        {onAskAI && (
          <button
            onClick={() => onAskAI(`What courses and credits are offered in ${selectedDept} semester ${selectedSem}?`)}
            className="px-3.5 py-2 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-200 text-xs font-medium flex items-center gap-2 transition-all self-start md:self-auto shrink-0 shadow-xs cursor-pointer"
          >
            <Compass className="w-3.5 h-3.5 text-zinc-400" />
            <span>Inquire About Semester {selectedSem}</span>
          </button>
        )}
      </div>

      {/* Selectors Panel */}
      <div className="p-4 sm:p-5 rounded-xl glass-panel space-y-4 bg-[var(--surface)] border border-[var(--line)]">
        {/* Department Pills */}
        <div className="space-y-1.5">
          <span className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-400" /> Department:
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            {departments.map(d => (
              <button
                key={d.id}
                aria-pressed={selectedDept === d.code}
                onClick={() => setSelectedDept(d.code)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  selectedDept === d.code
                    ? 'bg-[var(--ink)] text-zinc-950 font-semibold shadow-xs'
                    : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
                }`}
              >
                <span className="font-bold">{d.code}</span>
                <span className="hidden sm:inline ml-1.5">· {d.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Semester Stepper: Clean Segmented Control */}
        <div className="space-y-1.5 pt-3 border-t border-[var(--line)]">
          <span className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-zinc-400" /> Academic Semester:
          </span>
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
            {semesters.map(s => {
              const isSelected = selectedSem === s.num;
              return (
                <button
                  key={s.num}
                  aria-pressed={isSelected}
                  onClick={() => setSelectedSem(s.num)}
                  className={`py-2 px-2 rounded-lg text-xs font-semibold transition-all text-center cursor-pointer ${
                    isSelected
                      ? 'bg-[var(--ink)] text-zinc-950 shadow-xs'
                      : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  <span className="block text-[11px] font-bold">{s.label}</span>
                  <span className="block text-[10px] font-mono">Sem {s.num}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {semesterData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
            <div>
              <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block font-mono">
                Semester Total Credits
              </span>
              <div className="text-2xl sm:text-3xl font-extrabold text-[var(--ink)] mt-1">
                {semesterData.total_credits} <span className="text-xs font-semibold text-zinc-400">Credits</span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 mt-2">
              Assigned across <strong className="text-zinc-200 font-semibold">{semesterData.total_courses}</strong> official courses
            </p>
          </div>

          <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
            <div>
              <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block font-mono">
                Course Delivery Breakdown
              </span>
              <div className="text-2xl sm:text-3xl font-extrabold text-[var(--ink)] mt-1">
                <span className="text-zinc-100">{theoryCount}</span> <span className="text-xs font-semibold text-zinc-400">Theory</span>
                <span className="mx-2 text-zinc-600">·</span>
                <span className="text-emerald-400">{practicalCount}</span> <span className="text-xs font-semibold text-zinc-400">Lab</span>
              </div>
            </div>
            <p className="text-xs text-zinc-400 mt-2">
              Classroom lectures and practical laboratory coursework
            </p>
          </div>

          <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
            <div>
              <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block font-mono">
                Curriculum Categories
              </span>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {Object.entries(categoryCounts).map(([cat, cr]) => (
                  <span
                    key={cat}
                    className="px-2 py-0.5 rounded text-[11px] font-medium bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300 font-mono"
                  >
                    <strong className="text-zinc-200 font-semibold">{cat}:</strong> {cr} cr
                  </span>
                ))}
              </div>
            </div>
            <p className="text-xs text-zinc-400 mt-2">
              Distribution of MCC, MDC, AEC, and elective credits
            </p>
          </div>
        </div>
      )}

      {/* Course List Card */}
      <div className="rounded-xl bg-[var(--surface)] border border-[var(--line)] overflow-hidden shadow-xs">
        <div className="px-5 py-3.5 border-b border-[var(--line)] flex items-center justify-between bg-[var(--paper)]">
          <h3 className="text-sm font-bold text-[var(--ink)] flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-zinc-400" />
            <span>{selectedDept} — Semester {semesterData?.semester_roman || selectedSem} Curriculum</span>
          </h3>

          {semesterData?.source_page && (
            <button
              onClick={() => onViewSource(`DOC-${selectedDept}`, semesterData.source_page!)}
              className="text-xs font-medium text-zinc-300 hover:text-[var(--ink)] flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Official Handbook Page {semesterData.source_page}</span>
            </button>
          )}
        </div>

        {loadError ? (
          <div className="p-8 text-center text-rose-300 text-sm">{loadError}</div>
        ) : loading ? (
          <div className="p-12 text-center text-zinc-400 flex flex-col items-center justify-center gap-3">
            <div className="w-6 h-6 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs">Fetching semester curriculum records…</p>
          </div>
        ) : !semesterData || semesterData.courses.length === 0 ? (
          <div className="p-12 text-center text-zinc-400 text-xs">
            No courses found for this semester.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[var(--line)] text-[11px] font-semibold text-zinc-400 uppercase tracking-wider bg-[var(--paper)]">
                  <th className="py-3 px-4 font-semibold">Course Code</th>
                  <th className="py-3 px-4 font-semibold">Course Title</th>
                  <th className="py-3 px-3 text-center font-semibold">Category</th>
                  <th className="py-3 px-3 text-center font-semibold">L-T-P</th>
                  <th className="py-3 px-3 text-center font-semibold">Total Hours</th>
                  <th className="py-3 px-3 text-center font-semibold">Credits</th>
                  <th className="py-3 px-4 text-right font-semibold">Inquiries</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--line)] text-zinc-300">
                {semesterData.courses.map((course) => (
                  <tr key={course.code} className="hover:bg-[var(--ink)]/5 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-zinc-200 text-xs">
                      {course.code}
                    </td>
                    <td className="py-3 px-4 font-medium text-[var(--ink)] text-xs">
                      {course.title}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[var(--surface)] border border-[var(--line)] text-zinc-300 font-mono">
                        {course.category || 'Core'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-center font-mono text-xs text-zinc-400">
                      {course.lecture_hours}-{course.tutorial_hours}-{course.practical_hours}
                    </td>
                    <td className="py-3 px-3 text-center text-xs text-zinc-400">
                      {course.total_hours} hrs
                    </td>
                    <td className="py-3 px-3 text-center font-bold text-[var(--ink)] text-xs">
                      {course.credits.toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {onAskAI && (
                        <button
                          onClick={() => onAskAI(`What are the credits, contact hours, and syllabus for ${course.title} (${course.code})?`)}
                          className="px-2 py-1 rounded-md bg-[var(--surface-soft)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300 hover:text-[var(--ink)] text-[11px] font-medium inline-flex items-center gap-1 transition-colors cursor-pointer"
                        >
                          <MessageSquare className="w-3 h-3 text-zinc-400" />
                          <span>Inquire</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

