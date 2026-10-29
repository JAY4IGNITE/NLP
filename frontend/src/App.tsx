import React, { useState, useEffect } from 'react';
import { Navbar, type TabType } from './components/Navbar';
import { ChatView } from './components/ChatView';
import { ExploreView } from './components/ExploreView';
import { SemesterView } from './components/SemesterView';
import { CompareView } from './components/CompareView';
import { AdminView } from './components/AdminView';
import { CourseModal } from './components/CourseModal';
import { SourceModal } from './components/SourceModal';
import { LandingView } from './components/LandingView';

const readTab = (): TabType => {
  const tab = window.location.hash.slice(1);
  return ['chat', 'explore', 'semesters', 'compare', 'admin'].includes(tab) ? tab as TabType : 'home';
};

export const App: React.FC = () => {
  const [activeTab, updateActiveTab] = useState<TabType>(readTab);
  const setActiveTab = (tab: TabType) => {
    window.location.hash = tab;
    updateActiveTab(tab);
    window.scrollTo({ top: 0 });
  };
  useEffect(() => {
    const syncTab = () => updateActiveTab(readTab());
    window.addEventListener('hashchange', syncTab);
    return () => window.removeEventListener('hashchange', syncTab);
  }, []);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [sourceModal, setSourceModal] = useState<{ docId: string; page: number; title: string; dept: string } | null>(null);
  const [user] = useState<any>(() => {
    try {
      const saved = localStorage.getItem('campusai_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [pendingQuery, setPendingQuery] = useState<string>('');
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    // Apply the requested graphite appearance once, then retain subsequent choices.
    return localStorage.getItem('campusai_palette') === 'graphite' && localStorage.getItem('campusai_theme') === 'light' ? 'light' : 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    if (theme === 'light') {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.remove('light-theme');
      document.documentElement.classList.add('dark');
    }
    localStorage.setItem('campusai_theme', theme);
    localStorage.setItem('campusai_palette', 'graphite');
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleViewSource = (docId: string, page: number, title = 'Curriculum Regulation 2024', dept = 'Academic') => {
    setSourceModal({ docId, page, title, dept });
  };

  const handleAskAI = (query: string) => {
    setPendingQuery(query);
    setActiveTab('chat');
  };

  return (
    <div className={`app-shell flex flex-col font-sans ${activeTab === 'chat' ? 'chat-shell' : ''}`}>
      <a href="#main-content" className="skip-link" onClick={event => {
        event.preventDefault();
        document.getElementById('main-content')?.focus();
      }}>Skip to content</a>

      {/* Shared navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        theme={theme}
        onToggleTheme={toggleTheme}
        onAskAI={handleAskAI}
      />

      {/* Main View Area */}
      <main id="main-content" tabIndex={-1} className={`main-content flex-1 relative z-10 flex flex-col ${activeTab === 'chat' ? 'pb-0 overflow-hidden min-h-0' : 'pb-6 overflow-y-auto'}`}>
        {activeTab === 'home' && <LandingView onNavigate={setActiveTab} onAskAI={handleAskAI} />}
        <div hidden={activeTab !== 'chat'} className="chat-page view-enter h-full flex flex-col flex-1 min-h-0">
          <ChatView
            isActive={activeTab === 'chat'}
            onViewSource={handleViewSource}
            initialQuery={pendingQuery}
            onClearInitialQuery={() => setPendingQuery('')}
          />
        </div>

        {activeTab === 'explore' && (
          <ExploreView
            onSelectCourse={setSelectedCourseId}
            onViewSource={(docId, page) => handleViewSource(docId, page)}
            onAskAI={handleAskAI}
          />
        )}

        {activeTab === 'semesters' && (
          <SemesterView
            onViewSource={(docId, page) => handleViewSource(docId, page)}
            onAskAI={handleAskAI}
          />
        )}

        {activeTab === 'compare' && (
          <CompareView
            onAskAI={handleAskAI}
          />
        )}

        {activeTab === 'admin' && (
          <AdminView
            user={user}
          />
        )}
      </main>

      {/* Modals */}
      <CourseModal
        courseId={selectedCourseId}
        onClose={() => setSelectedCourseId(null)}
        onViewSource={handleViewSource}
        onAskAI={handleAskAI}
      />

      {sourceModal && (
        <SourceModal
          isOpen={true}
          docId={sourceModal.docId}
          pageNum={sourceModal.page}
          title={sourceModal.title}
          department={sourceModal.dept}
          onClose={() => setSourceModal(null)}
        />
      )}
    </div>
  );
};

export default App;
