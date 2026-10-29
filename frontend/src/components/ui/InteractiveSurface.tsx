import { type PointerEvent, type ReactNode } from 'react';
import { motion, useMotionValue, useSpring, useReducedMotion } from 'motion/react';

/** Small pointer-driven reflections give the glass depth without moving the form. */
export function InteractiveSurface({ children }: { children: ReactNode }) {
  const reducedMotion = useReducedMotion();
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const glowX = useSpring(x, { stiffness: 110, damping: 24 });
  const glowY = useSpring(y, { stiffness: 110, damping: 24 });
  function moveReflection(event: PointerEvent<HTMLDivElement>) {
    if (reducedMotion || event.pointerType !== 'mouse') return;
    const bounds = event.currentTarget.getBoundingClientRect();
    x.set((event.clientX - bounds.left - bounds.width / 2) * 0.35);
    y.set((event.clientY - bounds.top - bounds.height / 2) * 0.35);
  }
  return <motion.div className="question-panel"
    onPointerMove={moveReflection} onPointerLeave={() => { x.set(0); y.set(0); }}
    initial={reducedMotion ? false : { opacity: 0, y: 28, scale: 0.97 }}
    animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ type: 'spring', stiffness: 130, damping: 24, delay: 0.15 }}>
    <motion.div className="glass-reflection" aria-hidden="true" style={{ x: reducedMotion ? 0 : glowX, y: reducedMotion ? 0 : glowY }} />
    {children}
  </motion.div>;
}
