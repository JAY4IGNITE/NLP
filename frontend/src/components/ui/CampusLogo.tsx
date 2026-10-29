import { LibraryBig } from 'lucide-react';

export function CampusLogo({ className = '', reveal = false }: { className?: string; reveal?: boolean }) {
  return <LibraryBig strokeWidth={1.6} aria-hidden="true" className={`campus-logo ${reveal ? 'logo-reveal' : ''} ${className}`} />;
}
