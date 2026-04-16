'use client';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

export default function HeroSection() {
  return (
    <section
      id="hero"
      style={{
        position: 'relative',
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        background: 'transparent',
      }}
    >
      {/* ─── Top Navigation Bar ─── */}
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 20,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 40px',
        }}
      >
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'rgba(0, 240, 255, 0.08)',
              border: '1px solid rgba(0, 240, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M4 5h16M4 12h11M4 19h16" stroke="#00f0ff" strokeWidth="2" strokeLinecap="round" />
              <circle cx="18" cy="12" r="2" fill="#00f0ff" opacity="0.7" />
            </svg>
          </div>
          <span style={{
            fontSize: '15px',
            fontWeight: 700,
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.06em',
          }}>
            <span style={{ color: '#00f0ff' }}>EVENTRA</span>
            <span style={{ color: 'rgba(255,255,255,0.25)', margin: '0 1px' }}>-</span>
            <span style={{ color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>AI</span>
          </span>
        </div>

        {/* Nav Links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {['Agents', 'Workflow', 'Features'].map((item) => (
            <a
              key={item}
              href={`#${item.toLowerCase()}`}
              style={{
                fontSize: '11px',
                fontWeight: 500,
                color: '#00f0ff',
                textDecoration: 'none',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                fontFamily: 'var(--font-main)',
                padding: '7px 18px',
                borderRadius: '100px',
                border: '1px solid rgba(0, 240, 255, 0.2)',
                background: 'rgba(0, 240, 255, 0.06)',
                transition: 'all 0.25s ease',
                cursor: 'pointer',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(0, 240, 255, 0.12)';
                e.target.style.borderColor = 'rgba(0, 240, 255, 0.35)';
                e.target.style.boxShadow = '0 0 20px rgba(0, 240, 255, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(0, 240, 255, 0.06)';
                e.target.style.borderColor = 'rgba(0, 240, 255, 0.2)';
                e.target.style.boxShadow = 'none';
              }}
            >
              {item}
            </a>
          ))}

          <a
            href="#prompt"
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#00f0ff',
              textDecoration: 'none',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              fontFamily: 'var(--font-main)',
              padding: '7px 20px',
              borderRadius: '100px',
              border: '1px solid rgba(0, 240, 255, 0.2)',
              background: 'rgba(0, 240, 255, 0.06)',
              transition: 'all 0.25s ease',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(0, 240, 255, 0.12)';
              e.target.style.borderColor = 'rgba(0, 240, 255, 0.35)';
              e.target.style.boxShadow = '0 0 20px rgba(0, 240, 255, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(0, 240, 255, 0.06)';
              e.target.style.borderColor = 'rgba(0, 240, 255, 0.2)';
              e.target.style.boxShadow = 'none';
            }}
          >
            Get Started
          </a>
        </div>
      </motion.nav>

      {/* ─── Hero Content ─── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.4 }}
        style={{
          position: 'relative',
          zIndex: 5,
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Tagline chip */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          style={{
            fontSize: '11px',
            fontWeight: 500,
            fontFamily: 'var(--font-main)',
            color: 'rgba(0, 240, 255, 0.5)',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            padding: '6px 18px',
            borderRadius: '100px',
            border: '1px solid rgba(0, 240, 255, 0.1)',
            background: 'rgba(0, 240, 255, 0.03)',
            marginBottom: '32px',
          }}
        >
          AI-Powered Event Orchestration
        </motion.div>

        {/* Main heading */}
        <h1
          style={{
            fontSize: 'clamp(42px, 6.5vw, 76px)',
            fontWeight: 700,
            fontFamily: 'var(--font-display)',
            letterSpacing: '0.03em',
            textTransform: 'uppercase',
            lineHeight: 1.05,
            marginBottom: '20px',
          }}
        >
          <span style={{ color: '#ffffff' }}>Clarity</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.3)' }}>.</span>
          <span style={{ color: '#ffffff' }}> Focus</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.3)' }}>.</span>
          <span style={{ color: '#ffffff' }}> Impact</span>
          <span style={{ color: '#ffffff' }}>.</span>
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontSize: 'clamp(13px, 1.5vw, 16px)',
            fontWeight: 400,
            fontFamily: 'var(--font-main)',
            color: 'rgba(255, 255, 255, 0.3)',
            letterSpacing: '0.03em',
            maxWidth: '440px',
            lineHeight: 1.6,
            marginBottom: '40px',
          }}
        >
          We turn complex ideas into effortless experiences
        </p>

        {/* CTA Button */}
        <motion.a
          href="#prompt"
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '10px',
            padding: '14px 36px',
            background: 'rgba(0, 240, 255, 0.06)',
            border: '1px solid rgba(0, 240, 255, 0.18)',
            borderRadius: '100px',
            color: '#00f0ff',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: 600,
            fontFamily: 'var(--font-main)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            transition: 'all 0.3s ease',
            cursor: 'pointer',
          }}
        >
          Launch Agents
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '22px',
            height: '22px',
            borderRadius: '50%',
            background: 'rgba(0, 240, 255, 0.1)',
            fontSize: '12px',
          }}>→</span>
        </motion.a>
      </motion.div>

      {/* ─── Scroll Indicator ─── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.6 }}
        style={{
          position: 'absolute',
          bottom: '28px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
        }}
      >
        <motion.div
          animate={{ y: [0, 5, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ChevronDown size={16} color="rgba(255,255,255,0.15)" />
        </motion.div>
      </motion.div>
    </section>
  );
}
