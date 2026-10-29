import { useState, useRef, useEffect } from 'react';
import { BookOpenText, CalendarRange, Columns2, MessagesSquare, Moon, Settings2, Sun } from 'lucide-react';
import { CampusLogo } from './ui/CampusLogo';

export type TabType = 'home' | 'chat' | 'explore' | 'semesters' | 'compare' | 'admin';
interface NavbarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  user?: { role?: string } | null;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
  onAskAI: (query: string) => void;
}

export function Navbar({ activeTab, setActiveTab, user, theme, onToggleTheme, onAskAI }: NavbarProps) {
  const items = [
    { id: 'chat' as TabType, label: 'Assistant', icon: MessagesSquare },
    { id: 'explore' as TabType, label: 'Courses', icon: BookOpenText },
    { id: 'semesters' as TabType, label: 'Semesters', icon: CalendarRange },
    { id: 'compare' as TabType, label: 'Compare', icon: Columns2 },
    ...(user?.role === 'admin' ? [{ id: 'admin' as TabType, label: 'Admin', icon: Settings2 }] : []),
  ];

  function navigate(tab: TabType) { setActiveTab(tab); }

  const navRef = useRef<HTMLElement | null>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // 1. Apple sliding active pill state
  const [activePill, setActivePill] = useState({ left: 0, width: 0, opacity: 0 });

  // 2. Cursor tracking mirror duplicate pill & spotlight
  const [hoverPill, setHoverPill] = useState({ left: 0, width: 0, opacity: 0 });
  const [cursorPos, setCursorPos] = useState({ x: 0, y: 0, active: false });

  // Update active sliding pill whenever activeTab or items change
  useEffect(() => {
    const idx = items.findIndex(item => item.id === activeTab);
    if (idx >= 0 && tabRefs.current[idx] && navRef.current) {
      const tabEl = tabRefs.current[idx]!;
      const navEl = navRef.current;
      const tabRect = tabEl.getBoundingClientRect();
      const navRect = navEl.getBoundingClientRect();
      setActivePill({
        left: tabRect.left - navRect.left,
        width: tabRect.width,
        opacity: 1,
      });
    } else {
      setActivePill(prev => ({ ...prev, opacity: 0 }));
    }
  }, [activeTab, items.length]);

  // Recalculate on window resize
  useEffect(() => {
    const handleResize = () => {
      const idx = items.findIndex(item => item.id === activeTab);
      if (idx >= 0 && tabRefs.current[idx] && navRef.current) {
        const tabEl = tabRefs.current[idx]!;
        const navEl = navRef.current;
        const tabRect = tabEl.getBoundingClientRect();
        const navRect = navEl.getBoundingClientRect();
        setActivePill({
          left: tabRect.left - navRect.left,
          width: tabRect.width,
          opacity: 1,
        });
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [activeTab, items.length]);

  // Cursor tracking for mirror duplicate scrolling effect
  const handleMouseMove = (e: React.MouseEvent<HTMLElement>) => {
    if (!navRef.current) return;
    const rect = navRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCursorPos({ x, y, active: true });
  };

  const handleMouseLeave = () => {
    setCursorPos(prev => ({ ...prev, active: false }));
    setHoverPill(prev => ({ ...prev, opacity: 0 }));
  };

  const handleTabMouseEnter = (index: number) => {
    if (tabRefs.current[index] && navRef.current) {
      const tabEl = tabRefs.current[index]!;
      const navEl = navRef.current;
      const tabRect = tabEl.getBoundingClientRect();
      const navRect = navEl.getBoundingClientRect();
      setHoverPill({
        left: tabRect.left - navRect.left,
        width: tabRect.width,
        opacity: 1,
      });
    }
  };

  return (
    <header className="site-header">
      <div className="header-inner">
        <button className="brand flex items-center gap-3 text-left group cursor-pointer" aria-label="CampusAI Home" onClick={() => navigate('home')}>
          <span className="brand-symbol w-9 h-9 rounded-xl bg-gradient-to-br from-[#2997ff]/25 via-[#0071e3]/15 to-[#3b82f6]/25 border border-[#2997ff]/30 flex items-center justify-center text-[#2997ff] group-hover:scale-105 transition-all shadow-md shadow-blue-500/10">
            <CampusLogo className="w-5 h-5" />
          </span>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-heading font-bold text-lg tracking-tight text-[var(--ink)] leading-none">
                CampusAI
              </span>
              <span className="px-1.5 py-0.5 rounded-sm bg-[#2997ff]/15 border border-[#2997ff]/30 text-[9px] font-mono font-semibold text-[#2997ff] leading-none">
                AR24
              </span>
            </div>
            <span className="text-[10px] font-medium tracking-wider uppercase text-zinc-400 leading-tight mt-0.5">
              Aditya University
            </span>
          </div>
        </button>

        {/* Center: Fixed Static Dock with Apple sliding & cursor mirror duplicate effects */}
        {activeTab !== 'home' ? (
          <div className="header-center-dock" aria-label="Main navigation">
            <div className="dock-wrapper">
              <nav 
                ref={navRef}
                className="header-dock" 
                role="toolbar" 
                aria-label="Navigation dock"
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
              >
                {/* Dynamic mirror glare scrolling according to cursor */}
                <div 
                  className="dock-mirror-glare"
                  style={{
                    opacity: cursorPos.active ? 1 : 0,
                    background: `radial-gradient(130px circle at ${cursorPos.x}px ${cursorPos.y}px, rgba(255, 255, 255, 0.16), rgba(41, 151, 255, 0.08) 40%, transparent 80%)`,
                  }}
                  aria-hidden="true"
                />

                {/* Mirror duplicate hover pill scrolling according to cursor */}
                <div 
                  className="dock-hover-pill"
                  style={{
                    transform: `translateX(${hoverPill.left}px)`,
                    width: `${hoverPill.width}px`,
                    opacity: hoverPill.opacity,
                  }}
                  aria-hidden="true"
                />

                {/* Apple sliding active indicator pill */}
                <div 
                  className="dock-sliding-pill"
                  style={{
                    transform: `translateX(${activePill.left}px)`,
                    width: `${activePill.width}px`,
                    opacity: activePill.opacity,
                  }}
                  aria-hidden="true"
                />

                {/* Dock Feature Tabs */}
                {items.map(({ id, label, icon: Icon }, index) => {
                  const isActive = activeTab === id;
                  return (
                    <button
                      key={id}
                      ref={el => { tabRefs.current[index] = el; }}
                      type="button"
                      onClick={() => navigate(id)}
                      onMouseEnter={() => handleTabMouseEnter(index)}
                      onContextMenu={(e) => {
                        if (id === 'chat') {
                          e.preventDefault();
                          onAskAI('What are the minimum credit requirements for a B.Tech degree under Regulation 2024?');
                        } else if (id === 'explore') {
                          e.preventDefault();
                          onAskAI('How can I find course prerequisites in the curriculum?');
                        } else if (id === 'semesters') {
                          e.preventDefault();
                          onAskAI('What courses and credits are offered in CSE semester 1?');
                        } else if (id === 'compare') {
                          e.preventDefault();
                          onAskAI('Compare the CSE and IT curricula in semester 3.');
                        }
                      }}
                      className={`dock-tab ${isActive ? 'is-active' : ''}`}
                      aria-current={isActive ? 'page' : undefined}
                      title={`${label} (right-click for sample inquiry)`}
                    >
                      <Icon size={16} strokeWidth={isActive ? 2.1 : 1.75} className="dock-tab-icon" />
                      <span className="dock-tab-label">{label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>
        ) : (
          <div className="header-section-links">
            <a href="#academic-tools">Curriculum</a>
            <a href="#ask-campus">Assistant</a>
            <a href="#how-it-works">Sources</a>
          </div>
        )}

        {/* Right actions: Only dark/light toggle (hamburger button removed) */}
        <div className="header-actions flex items-center gap-2.5">
          <button
            className="p-2 rounded-xl text-zinc-400 hover:text-[var(--ink)] hover:bg-[var(--surface-soft)] border border-[var(--line)] transition-all cursor-pointer"
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>
        </div>
      </div>
    </header>
  );
}
