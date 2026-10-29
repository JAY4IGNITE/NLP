import React, { useState, useEffect } from 'react';
import {
  GitCompare, Layers, Calendar, CheckCircle2,
  Compass
} from 'lucide-react';
import { api } from '../api';
import type { Department, SemesterData } from '../types';

interface CompareViewProps {
  onAskAI?: (prompt: string) => void;
}

export const CompareView: React.FC<CompareViewProps> = ({ onAskAI }) => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [dept1, setDept1] = useState<string>('CSE');
  const [dept2, setDept2] = useState<string>('IT');
  const [semesterNum, setSemesterNum] = useState<number>(3);
  const [data1, setData1] = useState<SemesterData | null>(null);
  const [data2, setData2] = useState<SemesterData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getDepartments().then(setDepartments).catch(console.error);
  }, []);

  useEffect(() => {
    if (!dept1 || !dept2) return;
    setLoading(true);
    Promise.all([
      api.getSemester(dept1, semesterNum).catch(() => null),
      api.getSemester(dept2, semesterNum).catch(() => null)
    ]).then(([res1, res2]) => {
      setData1(res1);
      setData2(res2);
      setLoading(false);
    });
  }, [dept1, dept2, semesterNum]);

  // Compute common courses
  const codes1 = new Set(data1?.courses.map(c => c.code) || []);
  const codes2 = new Set(data2?.courses.map(c => c.code) || []);

  const commonCodes = new Set([...codes1].filter(x => codes2.has(x)));
  const uniqueToDept1 = data1?.courses.filter(c => !commonCodes.has(c.code)) || [];
  const uniqueToDept2 = data2?.courses.filter(c => !commonCodes.has(c.code)) || [];
  const commonCourses = data1?.courses.filter(c => commonCodes.has(c.code)) || [];

  return (
    <div className="workspace-view view-enter space-y-6 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-[var(--line)]">
        <div>
          <div className="text-[11px] font-bold text-zinc-400 tracking-wider uppercase flex items-center gap-1.5 font-mono">
            <GitCompare className="w-3.5 h-3.5" /> Explore the differences
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--ink)] mt-1 font-heading">
            Compare your curriculum
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-2xl">
            Analyze curricular overlaps, common core foundations, and specialized departmental courses between disciplines.
          </p>
        </div>

        {onAskAI && (
          <button
            onClick={() => onAskAI(`Compare the curriculum of ${dept1} and ${dept2} in semester ${semesterNum}. What are the major credit and syllabus differences?`)}
            className="px-3.5 py-2 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-200 text-xs font-medium flex items-center gap-2 transition-all self-start md:self-auto shrink-0 shadow-xs cursor-pointer"
          >
            <Compass className="w-3.5 h-3.5 text-zinc-400" />
            <span>Inquire About Cross-Branch Differences</span>
          </button>
        )}
      </div>

      {/* Selectors */}
      <div className="p-4 sm:p-5 rounded-xl glass-panel grid grid-cols-1 md:grid-cols-3 gap-4 items-center bg-[var(--surface)] border border-[var(--line)]">
        <div>
          <label className="block text-xs font-semibold text-zinc-400 mb-1.5 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-400" /> Primary Branch:
          </label>
          <select
            aria-label="Primary department"
            value={dept1}
            onChange={(e) => setDept1(e.target.value)}
            className="w-full glass-input px-3 py-2 text-xs font-semibold text-zinc-200 focus:outline-none transition-all bg-[var(--paper)] border border-[var(--line)]"
          >
            {departments.map(d => (
              <option key={d.id} value={d.code} className="bg-[var(--surface)] text-zinc-100">{d.code} — {d.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-400 mb-1.5 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-400" /> Comparison Branch:
          </label>
          <select
            aria-label="Comparison department"
            value={dept2}
            onChange={(e) => setDept2(e.target.value)}
            className="w-full glass-input px-3 py-2 text-xs font-semibold text-zinc-200 focus:outline-none transition-all bg-[var(--paper)] border border-[var(--line)]"
          >
            {departments.map(d => (
              <option key={d.id} value={d.code} className="bg-[var(--surface)] text-zinc-100">{d.code} — {d.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-zinc-400 mb-1.5 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-zinc-400" /> Academic Semester:
          </label>
          <select
            aria-label="Comparison semester"
            value={semesterNum}
            onChange={(e) => setSemesterNum(Number(e.target.value))}
            className="w-full glass-input px-3 py-2 text-xs font-semibold text-zinc-200 focus:outline-none transition-all bg-[var(--paper)] border border-[var(--line)]"
          >
            {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
              <option key={num} value={num} className="bg-[var(--surface)] text-zinc-100">Semester {num}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
          <div>
            <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block font-mono">
              {dept1} Total Credits
            </span>
            <div className="text-2xl sm:text-3xl font-extrabold text-[var(--ink)] mt-1">
              {data1?.total_credits ?? '—'} <span className="text-xs font-semibold text-zinc-400">Credits</span>
            </div>
          </div>
          <p className="text-xs text-zinc-400 mt-2">
            <strong className="text-zinc-200 font-semibold">{data1?.courses.length || 0}</strong> registered courses in Semester {semesterNum}
          </p>
        </div>

        <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
          <div>
            <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block font-mono">
              Identical Shared Core
            </span>
            <div className="text-2xl sm:text-3xl font-extrabold text-[var(--ink)] mt-1">
              {commonCodes.size} <span className="text-xs font-semibold text-zinc-400">Common Courses</span>
            </div>
          </div>
          <p className="text-xs text-zinc-400 mt-2">
            Harmonized syllabi and credit weights across both branches
          </p>
        </div>

        <div className="p-4 sm:p-5 rounded-xl bg-[var(--surface)] border border-[var(--line)] flex flex-col justify-between shadow-xs">
          <div>
            <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider block font-mono">
              {dept2} Total Credits
            </span>
            <div className="text-2xl sm:text-3xl font-extrabold text-[var(--ink)] mt-1">
              {data2?.total_credits ?? '—'} <span className="text-xs font-semibold text-zinc-400">Credits</span>
            </div>
          </div>
          <p className="text-xs text-zinc-400 mt-2">
            <strong className="text-zinc-200 font-semibold">{data2?.courses.length || 0}</strong> registered courses in Semester {semesterNum}
          </p>
        </div>
      </div>

      {/* 3-Column Diff Layout */}
      {loading ? (
        <div className="p-12 text-center text-zinc-400 flex flex-col items-center justify-center gap-3">
          <div className="w-6 h-6 border-2 border-zinc-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs">Analyzing curricula between {dept1} and {dept2}…</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Column 1: Exclusive to Dept 1 */}
          <div className="rounded-xl bg-[var(--surface)] border border-[var(--line)] p-4 sm:p-5 space-y-3.5 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
              <span className="text-xs font-bold text-zinc-200 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-zinc-400 shadow-xs" />
                Exclusive to {dept1} ({uniqueToDept1.length})
              </span>
            </div>

            <div className="space-y-2.5">
              {uniqueToDept1.length === 0 ? (
                <p className="text-xs text-zinc-500 italic p-4 text-center">
                  All courses in {dept1} are shared with {dept2} in Semester {semesterNum}.
                </p>
              ) : (
                uniqueToDept1.map(course => (
                  <div key={course.code} className="p-3.5 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] space-y-1.5 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-zinc-200">{course.code}</span>
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-200">
                        {course.credits.toFixed(1)} Cr
                      </span>
                    </div>
                    <h4 className="text-xs font-semibold text-[var(--ink)]">{course.title}</h4>
                    <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                      <span>Category: <strong className="text-zinc-300 font-mono">{course.category || 'Core'}</strong></span>
                      <span>·</span>
                      <span>Hours: <strong className="text-zinc-300">{course.total_hours} hrs</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 2: Shared Courses */}
          <div className="rounded-xl bg-[var(--surface)] border border-[var(--line)] p-4 sm:p-5 space-y-3.5 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Shared Common Core ({commonCourses.length})
              </span>
            </div>

            <div className="space-y-2.5">
              {commonCourses.length === 0 ? (
                <p className="text-xs text-zinc-500 italic p-4 text-center">
                  No identical course codes between {dept1} and {dept2} in Semester {semesterNum}.
                </p>
              ) : (
                commonCourses.map(course => (
                  <div key={course.code} className="p-3.5 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] space-y-1.5 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-emerald-400">{course.code}</span>
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-[var(--surface)] text-emerald-300 border border-[var(--line)] font-mono">
                        {course.credits.toFixed(1)} Cr
                      </span>
                    </div>
                    <h4 className="text-xs font-semibold text-[var(--ink)]">{course.title}</h4>
                    <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                      <span>Category: <strong className="text-zinc-300 font-mono">{course.category || 'Core'}</strong></span>
                      <span>·</span>
                      <span>Hours: <strong className="text-zinc-300">{course.total_hours} hrs</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 3: Exclusive to Dept 2 */}
          <div className="rounded-xl bg-[var(--surface)] border border-[var(--line)] p-4 sm:p-5 space-y-3.5 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--line)]">
              <span className="text-xs font-bold text-zinc-300 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-zinc-500" />
                Exclusive to {dept2} ({uniqueToDept2.length})
              </span>
            </div>

            <div className="space-y-2.5">
              {uniqueToDept2.length === 0 ? (
                <p className="text-xs text-zinc-500 italic p-4 text-center">
                  All courses in {dept2} are shared with {dept1} in Semester {semesterNum}.
                </p>
              ) : (
                uniqueToDept2.map(course => (
                  <div key={course.code} className="p-3.5 rounded-lg bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] space-y-1.5 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-zinc-200">{course.code}</span>
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-200">
                        {course.credits.toFixed(1)} Cr
                      </span>
                    </div>
                    <h4 className="text-xs font-semibold text-[var(--ink)]">{course.title}</h4>
                    <div className="flex items-center gap-2 text-[11px] text-zinc-400">
                      <span>Category: <strong className="text-zinc-300 font-mono">{course.category || 'Core'}</strong></span>
                      <span>·</span>
                      <span>Hours: <strong className="text-zinc-300">{course.total_hours} hrs</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

