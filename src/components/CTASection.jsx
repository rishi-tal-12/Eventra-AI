'use client';
import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function CTASection() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <section
      id="cta"
      ref={ref}
      style={{ padding: '120px 0', position: 'relative' }}
    >
      <div className="container" style={{ maxWidth: '800px' }}>
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          style={{
            position: 'relative',
            textAlign: 'center',
            padding: '72px 40px',
            borderRadius: '32px',
            overflow: 'hidden',
            background: 'rgba(15, 15, 35, 0.4)',
            border: '1px solid rgba(139, 92, 246, 0.15)',
          }}
        >
          {/* Gradient background blobs */}
          <div
            style={{
              position: 'absolute',
              top: '-50%',
              left: '-20%',
              width: '300px',
              height: '300px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%)',
              filter: 'blur(60px)',
              pointerEvents: 'none',
            }}
          />
          <div
            style={{
              position: 'absolute',
              bottom: '-40%',
              right: '-10%',
              width: '350px',
              height: '350px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%)',
              filter: 'blur(60px)',
              pointerEvents: 'none',
            }}
          />

          <motion.div
            initial={{ scale: 0 }}
            animate={isInView ? { scale: 1 } : {}}
            transition={{ delay: 0.3, type: 'spring' }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '64px',
              height: '64px',
              borderRadius: '20px',
              background: 'linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15))',
              border: '1px solid rgba(139,92,246,0.2)',
              marginBottom: '28px',
            }}
          >
            <Sparkles size={28} color="#8b5cf6" />
          </motion.div>

          <h2
            style={{
              fontSize: 'clamp(28px, 4vw, 48px)',
              fontWeight: 800,
              fontFamily: 'var(--font-display)',
              lineHeight: 1.15,
              marginBottom: '16px',
              position: 'relative',
            }}
          >
            Ready to Plan Your
            <br />
            <span className="animated-gradient-text">Perfect Event?</span>
          </h2>

          <p
            style={{
              fontSize: '17px',
              color: 'var(--text-secondary)',
              maxWidth: '480px',
              margin: '0 auto 36px',
              lineHeight: 1.6,
              position: 'relative',
            }}
          >
            Let our 8 AI agents handle the complexity while you focus on what matters — 
            creating unforgettable experiences.
          </p>

          <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', position: 'relative', flexWrap: 'wrap' }}>
            <motion.a
              href="#prompt"
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.98 }}
              className="btn-primary"
              style={{ textDecoration: 'none', padding: '16px 36px', fontSize: '16px' }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                Start Planning Now
                <ArrowRight size={18} />
              </span>
            </motion.a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
