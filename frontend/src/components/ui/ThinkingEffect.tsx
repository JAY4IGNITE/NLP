import { ChevronDown, Clock } from 'lucide-react';

interface ThinkingActiveProps { elapsedSeconds: number; }
export function ThinkingActive({ elapsedSeconds }: ThinkingActiveProps) {
  return <div className="thinking-status" role="status" aria-live="polite">
    <span className="thinking-dots" aria-hidden="true"><i /><i /><i /></span>
    <span>Preparing your answer</span>
    <span className="thinking-elapsed" aria-hidden="true">{Math.floor(elapsedSeconds)}s</span>
  </div>;
}

interface ThinkingAccordionProps { duration?: number; intent?: string; domain?: string; isGrounded?: boolean; }
export function ThinkingAccordion({ duration = 0, intent, domain, isGrounded }: ThinkingAccordionProps) {
  return <details className="response-details">
    <summary><Clock size={13} /><span>Response details</span><span>{duration.toFixed(1)}s</span><ChevronDown size={13} /></summary>
    <dl>
      {intent && <div><dt>Topic</dt><dd>{intent.replaceAll('_', ' ')}</dd></div>}
      {domain && <div><dt>Area</dt><dd>{domain.replaceAll('_', ' ')}</dd></div>}
      <div><dt>Curriculum</dt><dd>Aditya University · Regulation 2024</dd></div>
      <div><dt>Source check</dt><dd>{isGrounded ? 'Reported as grounded by the service. Review original sources.' : 'Source grounding was not confirmed.'}</dd></div>
    </dl>
  </details>;
}
