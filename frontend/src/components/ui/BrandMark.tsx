import { useEffect, useRef, useId } from 'react';

export interface BrandMarkProps {
  className?: string;
  animate?: boolean;
  state?: 'idle' | 'static' | 'thinking';
}

export function BrandMark({ className = '', animate = true, state }: BrandMarkProps) {
  const containerRef = useRef<SVGSVGElement | null>(null);
  const eyesRef = useRef<SVGGElement | null>(null);
  const rawId = useId();
  const maskId = `eyes-mask-${rawId.replace(/:/g, '')}`;

  const currentState = state || (animate ? 'idle' : 'static');

  useEffect(() => {
    if (currentState === 'static') return;
    
    let animationFrameId: number;
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    let targetScale = 1;
    let currentScale = 1;
    let blinkTimeout: any;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current || currentState !== 'idle') return;
      
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;
      
      const angle = Math.atan2(deltaY, deltaX);
      const maxMove = 3;
      
      const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 80, 1) * maxMove;
      
      targetX = Math.cos(angle) * distance;
      targetY = Math.sin(angle) * distance;
    };

    const scheduleBlink = () => {
      if (currentState !== 'idle') return;
      targetScale = 0.1;
      setTimeout(() => {
        targetScale = 1;
      }, 150);
      blinkTimeout = setTimeout(scheduleBlink, 3000 + Math.random() * 5000);
    };

    if (currentState === 'idle') {
      window.addEventListener('mousemove', handleMouseMove);
      blinkTimeout = setTimeout(scheduleBlink, 2000);
    }

    const animationLoop = () => {
      if (currentState === 'thinking') {
        const time = Date.now();
        targetX = Math.sin(time / 250) * 4;
        targetY = Math.abs(Math.cos(time / 250)) * 2 - 1;
        targetScale = 1;
      }

      currentX += (targetX - currentX) * 0.12;
      currentY += (targetY - currentY) * 0.12;
      currentScale += (targetScale - currentScale) * 0.3;
      
      if (eyesRef.current) {
        eyesRef.current.style.transform = `translate(${currentX}px, ${currentY}px) scaleY(${currentScale})`;
      }
      animationFrameId = requestAnimationFrame(animationLoop);
    };

    animationLoop();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
      clearTimeout(blinkTimeout);
    };
  }, [currentState]);

  return (
    <svg 
      ref={containerRef}
      className={`brand-mark ${className}`} 
      viewBox="0 0 32 32" 
      fill="none" 
      aria-hidden="true"
    >
      <defs>
        <mask id={maskId}>
          <rect x="0" y="0" width="32" height="32" fill="white" />
          <g ref={eyesRef} style={{ willChange: 'transform', transformOrigin: '16px 16px' }}>
            <circle cx="11" cy="16" r="3.5" fill="black" />
            <circle cx="21" cy="16" r="3.5" fill="black" />
          </g>
        </mask>
      </defs>
      <circle cx="16" cy="16" r="16" fill="currentColor" mask={`url(#${maskId})`} />
    </svg>
  );
}

export default BrandMark;
