import React, { useState, useEffect } from 'react';
import {
  Search, Filter, BookOpen, ExternalLink,
  Layers, Award, Clock, MessageSquare, ChevronRight
} from 'lucide-react';
import { api } from '../api';
import type { Course, Department } from '../types';

interface ExploreViewProps {
  onSelectCourse: (courseId: number) => void;
  onViewSource: (docId: string, page: number) => void;
  onAskAI?: (prompt: string) => void;
}

export const ExploreView: React.FC<ExploreViewProps> = ({
  onSelectCourse,
  onViewSource,
  onAskAI
}) => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDept, setSelectedDept] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCredit, setSelectedCredit] = useState<string>('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    api.getDepartments().then(setDepartments).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    setLoadError('');
    const delayDebounce = setTimeout(() => {
      api.getCourses(selectedDept || undefined, searchQuery || undefined, 120)
        .then(data => {
          setCourses(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoadError('The course catalog could not be loaded. Please check your connection and retry.');
          setLoading(false);
        });
    }, 250);

    return () => clearTimeout(delayDebounce);
  }, [selectedDept, searchQuery]);

  const categories = ['All', 'MCC', 'MDC', 'AEC', 'VAC', 'SEC', 'PE', 'OE', 'MC'];
  const creditOptions = ['All', '1', '2', '3', '4', '6'];

  const filteredCourses = courses.filter(c => {
    const matchCat = !selectedCategory || selectedCategory === 'All'
      || c.category?.toUpperCase() === selectedCategory.toUpperCase();
    const matchCred = !selectedCredit || selectedCredit === 'All'
      || Math.round(c.credits) === parseInt(selectedCredit, 10);
    return matchCat && matchCred;
  });

  return (
    <div className="workspace-view view-enter space-y-6 max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-[var(--line)]">
        <div>
          <div className="text-[11px] font-bold text-zinc-400 tracking-wider uppercase flex items-center gap-1.5 font-mono">
            <BookOpen className="w-3.5 h-3.5" /> Find your next course
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--ink)] mt-1 font-heading">
            Course catalog
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-2xl">
            Explore accredited B.Tech courses across 8 engineering disciplines under Academic Regulation 2024 (Version 3.0).
          </p>
        </div>

        <div className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[var(--surface)] border border-[var(--line)] text-zinc-300 shrink-0 self-start md:self-auto shadow-xs">
          Showing <span className="text-[var(--ink)] font-bold">{filteredCourses.length}</span> verified courses
        </div>
      </div>

      {/* Filter and Search Panel */}
      <div className="p-4 sm:p-5 rounded-xl glass-panel space-y-4 bg-[var(--surface)] border border-[var(--line)]">
        {/* Search Input with BorderBeam */}
        <div className="relative w-full rounded-full">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
              <input
                type="search"
                aria-label="Search courses"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by course title, code (e.g. 241MA001, 241CS001), or topic…"
                className="w-full text-sm text-zinc-100 placeholder-zinc-500 pl-11 pr-5 py-3 rounded-full focus:outline-none transition-all bg-[var(--paper)] border border-[var(--line)] focus:border-zinc-500 shadow-inner"
              />
            </div>
          
        </div>

        {/* Department Pills */}
        <div className="space-y-1.5">
          <span className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-400" /> Department:
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setSelectedDept('')}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                selectedDept === ''
                  ? 'bg-[var(--ink)] text-zinc-950 font-semibold shadow-xs'
                  : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
              }`}
            >
              All Departments
            </button>
            {departments.map(d => (
              <button
                key={d.id}
                onClick={() => setSelectedDept(d.code)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer ${
                  selectedDept === d.code
                    ? 'bg-[var(--ink)] text-zinc-950 font-semibold shadow-xs'
                    : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {d.code}
              </button>
            ))}
          </div>
        </div>

        {/* Category & Credits Row */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-[var(--line)] text-xs">
          {/* Category Filter */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="font-semibold text-zinc-400 shrink-0 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5 text-zinc-400" /> Category:
            </span>
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat === 'All' ? '' : cat)}
                className={`px-2 py-0.5 rounded text-xs font-medium transition-colors cursor-pointer ${
                  (selectedCategory === cat || (!selectedCategory && cat === 'All'))
                    ? 'bg-[var(--surface-soft)] text-[var(--ink)] border border-[var(--line)] font-semibold'
                    : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {cat === 'All' ? 'All' : cat}
              </button>
            ))}
          </div>

          {/* Credits Filter */}
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="font-semibold text-zinc-400 flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-zinc-400" /> Credits:
            </span>
            {creditOptions.map(c => (
              <button
                key={c}
                onClick={() => setSelectedCredit(c === 'All' ? '' : c)}
                className={`px-2 py-0.5 rounded text-xs font-medium transition-colors cursor-pointer ${
                  (selectedCredit === c || (!selectedCredit && c === 'All'))
                    ? 'bg-[var(--ink)] text-zinc-950 font-semibold shadow-xs'
                    : 'bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-400 hover:text-zinc-200'
                }`}
              >
                {c === 'All' ? 'All' : `${c} Cr`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Course Grid */}
      {loadError ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {loadError}
        </div>
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-44 rounded-xl bg-[var(--surface)] border border-[var(--line)] animate-pulse" />
          ))}
        </div>
      ) : filteredCourses.length === 0 ? (
        <div className="p-12 text-center rounded-xl bg-[var(--surface)] border border-[var(--line)] text-zinc-400">
          <BookOpen className="w-8 h-8 mx-auto mb-2 text-zinc-600" />
          <h3 className="text-sm font-semibold text-zinc-300">No courses match your filter criteria</h3>
          <p className="text-xs text-zinc-500 mt-1">Try resetting the category filter or searching for another course title.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCourses.map(course => (
            <div
              key={course.id}
              className="group flex flex-col justify-between p-4 sm:p-5 rounded-xl bg-[var(--surface)] hover:bg-[var(--surface-soft)] border border-[var(--line)] hover:border-[var(--line)] transition-all shadow-xs"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-[var(--surface-soft)] text-zinc-200 border border-[var(--line)]">
                    {course.code}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {course.category && (
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300 font-mono">
                        {course.category}
                      </span>
                    )}
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-200">
                      {course.credits.toFixed(1)} Cr
                    </span>
                  </div>
                </div>

                <h3 className="font-semibold text-zinc-100 group-hover:text-[var(--ink)] transition-colors line-clamp-2 text-sm leading-snug">
                  <button onClick={() => onSelectCourse(course.id)} className="text-left w-full cursor-pointer">
                    {course.title}
                  </button>
                </h3>

                {course.department_code && (
                  <p className="text-xs text-zinc-400 mt-1 font-medium">
                    {course.department_code} Department
                  </p>
                )}

                <div className="mt-3 flex items-center gap-2 text-xs text-zinc-400">
                  <Clock className="w-3.5 h-3.5 text-zinc-500" />
                  <span>L-T-P: <strong className="text-zinc-200">{course.lecture_hours}-{course.tutorial_hours}-{course.practical_hours}</strong></span>
                  <span>·</span>
                  <span>Total: <strong className="text-zinc-200">{course.total_hours} hrs</strong></span>
                </div>
              </div>

              {/* Action Links */}
              <div className="mt-4 pt-3 border-t border-[var(--line)] flex items-center justify-between gap-2 text-xs">
                <button
                  onClick={() => onSelectCourse(course.id)}
                  className="font-medium text-zinc-300 hover:text-[var(--ink)] flex items-center gap-1 cursor-pointer"
                >
                  <span>Syllabus & Books</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>

                <div className="flex items-center gap-1.5">
                  {course.source_document_id && course.source_page && (
                    <button
                      onClick={() => onViewSource(course.source_document_id!, course.source_page!)}
                      className="p-1.5 rounded-lg bg-[var(--surface-soft)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300 hover:text-[var(--ink)] transition-colors cursor-pointer"
                      title={`Open official handbook page ${course.source_page}`}
                      aria-label={`View official handbook page ${course.source_page} for ${course.title}`}
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  )}

                  {onAskAI && (
                    <button
                      onClick={() => onAskAI(`What are the credits and prerequisites for ${course.title} (${course.code})?`)}
                      className="p-1.5 rounded-lg bg-[var(--surface-soft)] hover:bg-[var(--surface-soft)] border border-[var(--line)] text-zinc-300 hover:text-[var(--ink)] transition-colors cursor-pointer"
                      title="Ask CampusAI about this course"
                      aria-label={`Ask AI about ${course.title}`}
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
