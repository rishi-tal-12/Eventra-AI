'use client';
import { useEffect, useRef } from 'react';

export default function MouseGlow() {
  const glowRef = useRef(null);

  useEffect(() => {
    const glow = glowRef.current;
    if (!glow) return;

    let rafId;
    let mouseX = -1000, mouseY = -1000;

    const handleMouseMove = (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    const animate = () => {
      glow.style.left = mouseX + 'px';
      glow.style.top = mouseY + 'px';
      rafId = requestAnimationFrame(animate);
    };

    document.addEventListener('mousemove', handleMouseMove);
    rafId = requestAnimationFrame(animate);

    // Also update spotlight card CSS vars
    const handleCardSpotlight = (e) => {
      const cards = document.querySelectorAll('.spotlight-card');
      cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--x', x + '%');
        card.style.setProperty('--y', y + '%');
      });
    };
    document.addEventListener('mousemove', handleCardSpotlight);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mousemove', handleCardSpotlight);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return <div ref={glowRef} className="mouse-glow" />;
}
