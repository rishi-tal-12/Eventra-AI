'use client';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Users, Zap, Calendar } from 'lucide-react';

const navItems = [
  { icon: Sparkles, label: 'Home', href: '#hero' },
  { icon: Users, label: 'Agents', href: '#agents' },
  { icon: Zap, label: 'Launch', href: '#prompt' },
  { icon: Calendar, label: 'Workflow', href: '#workflow' },
];

export default function FloatingNav() {
  const [hoveredIdx, setHoveredIdx] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <AnimatePresence>
      {visible && (
        <motion.nav
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 25 }}
          style={{
            position: 'fixed',
            bottom: '28px',
            left: 0,
            right: 0,
            margin: '0 auto',
            width: 'fit-content',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '8px 12px',
            background: 'rgba(10, 10, 30, 0.85)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(0, 240, 255, 0.15)',
            borderRadius: '20px',
            boxShadow: '0 8px 40px rgba(0,0,0,0.5), 0 0 20px rgba(0, 240, 255, 0.08)',
          }}
        >
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            const isHovered = hoveredIdx === idx;
            return (
              <motion.a
                key={item.label}
                href={item.href}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
                animate={{ scale: isHovered ? 1.25 : 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '2px',
                  padding: '10px 14px',
                  borderRadius: '14px',
                  textDecoration: 'none',
                  color: isHovered ? '#00f0ff' : 'rgba(200,200,240,0.6)',
                  background: isHovered ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                  transition: 'color 0.2s, background 0.2s',
                  position: 'relative',
                }}
              >
                <Icon size={20} />
                <AnimatePresence>
                  {isHovered && (
                    <motion.span
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 4 }}
                      style={{
                        fontSize: '10px',
                        fontWeight: 600,
                        whiteSpace: 'nowrap',
                        position: 'absolute',
                        top: '-28px',
                        background: 'rgba(10,10,30,0.9)',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        border: '1px solid rgba(0,240,255,0.2)',
                      }}
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.a>
            );
          })}
        </motion.nav>
      )}
    </AnimatePresence>
  );
}
