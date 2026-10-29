import { useState, type FormEvent } from 'react';
import { ArrowUp, ArrowUpRight, BookOpenText, ChevronRight, Columns2, FileText, Languages, MessageSquare, Search } from 'lucide-react';
import { motion, useReducedMotion } from 'motion/react';
import type { TabType } from './Navbar';
import { CampusLogo } from './ui/CampusLogo';
import { InteractiveSurface } from './ui/InteractiveSurface';

interface LandingViewProps {
  onNavigate: (tab: TabType) => void;
  onAskAI: (query: string) => void;
}

const resources = [
  { tab: 'explore' as const, title: 'Every course. In detail.', description: 'Syllabi, learning outcomes, textbooks, and credits. Get the complete picture before your next class.', action: 'Explore the catalog', image: 'course-library', alt: 'Sculptural glass reference books with a cobalt-blue volume' },
  { tab: 'semesters' as const, title: 'See the semester ahead.', description: 'Follow your course sequence and credit requirements, from your first semester to your final year.', action: 'View semester plans', image: 'semester-sequence', alt: 'Eight glass plates arranged in an orderly semester sequence' },
];
const prompts = ['How many credits do I need to graduate?', 'What are the attendance requirements?', 'What will I study in CSE semester 1?'];

export function LandingView({ onNavigate, onAskAI }: LandingViewProps) {
  const [question, setQuestion] = useState('');
  const reducedMotion = useReducedMotion();
  const reveal = {
    initial: reducedMotion ? false as const : { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.65 },
  };
  function submit(event: FormEvent) {
    event.preventDefault();
    if (question.trim()) onAskAI(question.trim());
  }

  return <div className="design-home">
    <section className="design-hero" aria-labelledby="landing-title">
      <motion.div className="design-copy design-container" initial={reducedMotion ? false : { opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
        <p className="design-kicker">CampusAI for Aditya University</p>
        <h1 className="design-title" id="landing-title">Your curriculum.<br />Made clear.</h1>
        <p className="design-intro">Explore what you’ll learn. Plan what comes next.<br className="desktop-break" /> Get answers grounded in your university’s academic documents.</p>
        <div className="design-actions">
          <button className="button-primary" onClick={() => onNavigate('chat')}>Ask CampusAI</button>
          <button className="design-link" onClick={() => onNavigate('explore')}>Explore courses <ChevronRight size={17} /></button>
        </div>
      </motion.div>
      <motion.figure className="design-hero-art design-container" initial={reducedMotion ? false : { opacity: 0, y: 26 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.85, delay: 0.12 }}>
        <img src="/visuals/curriculum-glass.webp" alt="An open glass book, calendar, and magnifying lens with cool blue refracted light" width="1536" height="1024" fetchPriority="high" />
      </motion.figure>
      <p className="design-hero-caption">Built around B.Tech Regulation 2024 <span aria-hidden="true">·</span> English & Telugu</p>
    </section>

    <motion.section {...reveal} id="academic-tools" className="design-resources design-container" aria-labelledby="tools-heading">
      <div className="design-section-heading">
        <h2 id="tools-heading">Know your curriculum.<br /><span>Find your next step.</span></h2>
        <p>The details that matter, brought together.<br />From a single course to the full degree.</p>
      </div>
      <div className="design-resource-grid">
        {resources.map(resource => <article className="design-resource" key={resource.tab}>
          <button className="design-resource-image" onClick={() => onNavigate(resource.tab)} aria-label={resource.tab === 'explore' ? 'Browse course catalog' : 'Browse semester plans'}>
            <img src={'/visuals/' + resource.image + '.webp'} alt={resource.alt} width="1536" height="1024" loading="lazy" />
          </button>
          <div className="design-resource-copy">
            <h3>{resource.title}</h3>
            <p>{resource.description}</p>
            <button className="design-link" onClick={() => onNavigate(resource.tab)}>{resource.action}<ChevronRight size={17} /></button>
          </div>
        </article>)}
      </div>
      <div className="design-compare">
        <div className="design-compare-left">
          <span className="design-compare-icon">
            <Columns2 size={22} aria-hidden="true" />
          </span>
          <div className="design-compare-text">
            <h3>Different branches. A side-by-side view.</h3>
            <p>See the courses and requirements that connect each discipline.</p>
          </div>
        </div>
        <button className="design-link" onClick={() => onNavigate('compare')}>
          Compare branches <ChevronRight size={17} />
        </button>
      </div>
    </motion.section>

    <section className="design-assistant-band" id="ask-campus" aria-labelledby="assistant-heading">
      <div className="design-assistant design-container">
        <motion.div {...reveal} className="design-assistant-copy">
          <p className="design-kicker">The academic assistant</p>
          <h2 id="assistant-heading">A good question.<br />A clearer answer.</h2>
          <p>Ask about credits, attendance, or a course. CampusAI helps you find the relevant details and points you back to the source.</p>
          <div className="design-language"><Languages size={18} />Ask in English, Telugu, or both.</div>
          <div>
            <button className="design-link" onClick={() => onNavigate('chat')}>Start a conversation <ChevronRight size={17} /></button>
          </div>
        </motion.div>
        <InteractiveSurface>
          <div className="design-question-heading"><MessageSquare size={19} /><span>Ask CampusAI</span><span className="design-question-edition">R24</span></div>
          <div className="design-question-body">
            <form onSubmit={submit} className="landing-question-form">
              <label htmlFor="landing-question">What would you like to understand?</label>
              <textarea id="landing-question" aria-label="Your academic question" value={question} onChange={event => setQuestion(event.target.value)} placeholder="Ask about a course, credits, or a regulation…" rows={3} required maxLength={2000} />
              <div><span>Ask in your own words</span><button type="submit" aria-label="Ask this question" disabled={!question.trim()}><ArrowUp size={18} /></button></div>
            </form>
            <p className="design-prompt-label">A few places to start</p>
            {prompts.map(prompt => <button className="landing-prompt" key={prompt} onClick={() => onAskAI(prompt)}>{prompt}<ArrowUpRight size={15} /></button>)}
          </div>
          <div className="design-question-footer"><BookOpenText size={15} />Based on academic documents. Check the original source.</div>
        </InteractiveSurface>
      </div>
    </section>

    <motion.section {...reveal} id="how-it-works" className="design-sources design-container" aria-labelledby="source-heading">
      <div className="design-section-heading">
        <h2 id="source-heading">Clarity comes<br /><span>with context.</span></h2>
        <p>A useful answer should help you understand<br />where the information comes from.</p>
      </div>
      <ol className="design-source-steps">
        <li>
          <div className="design-step-badge">
            <MessageSquare size={22} />
          </div>
          <h3>Ask naturally.</h3>
          <p>Start with a question about your curriculum. No special commands or keywords needed.</p>
        </li>
        <li>
          <div className="design-step-badge">
            <Search size={22} />
          </div>
          <h3>Understand the details.</h3>
          <p>Read an explanation based on the available curriculum and academic records.</p>
        </li>
        <li>
          <div className="design-step-badge">
            <FileText size={22} />
          </div>
          <h3>Review the source.</h3>
          <p>Open available page citations and check the university document for yourself.</p>
        </li>
      </ol>
      <div className="design-sources-action">
        <button className="button-primary flex items-center gap-2" onClick={() => onNavigate('chat')}>
          Find your first answer <ChevronRight size={17} />
        </button>
      </div>
    </motion.section>

    <footer className="design-footer">
      <div className="design-footer-inner">
        <div className="design-footer-brand">
          <span className="brand-symbol w-7 h-7 rounded-lg bg-gradient-to-br from-[#2997ff]/25 via-[#0071e3]/15 to-[#3b82f6]/25 border border-[#2997ff]/30 flex items-center justify-center text-[#2997ff]">
            <CampusLogo className="w-4 h-4" />
          </span>
          <strong>CampusAI</strong>
          <span className="design-footer-sep">·</span>
          <span>Aditya University Academic Intelligence</span>
        </div>
        <div className="design-footer-links">
          <button onClick={() => onNavigate('explore')}>Course catalog</button>
          <a href="#academic-tools">Curriculum</a>
          <a href="#how-it-works">Sources</a>
          <span className="px-2 py-0.5 rounded bg-[#2997ff]/10 text-[#2997ff] text-[10px] font-mono border border-[#2997ff]/20">B.Tech · R24</span>
        </div>
      </div>
    </footer>
  </div>;
}

