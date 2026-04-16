'use client';
import { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform, useInView } from 'framer-motion';
import { Zap, ShieldCheck, Clock, LineChart, Globe, Users } from 'lucide-react';

const features = [
  {
    title: 'LIGHTNING FAST',
    description: 'All 8 agents work in parallel, delivering fully optimized event strategies in minutes instead of weeks.',
    icon: Zap,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800',
  },
  {
    title: 'DATA-DRIVEN',
    description: 'Every recommendation is backed by live data ingestion from past events, sentiment analysis, and market trends.',
    icon: ShieldCheck,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=800',
  },
  {
    title: 'REAL-TIME SYNC',
    description: 'Watch the orchestration live. Swap parameters on the fly and watch the neural network recalibrate instantly.',
    icon: Clock,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800',
  },
  {
    title: 'OPTIMIZATION',
    description: 'Advanced financial modeling runs thousands of ticket tier simulations to guarantee break-even margins.',
    icon: LineChart,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800',
  },
  {
    title: 'GLOBAL SCALABILITY',
    description: 'From local meetups to massive expos, scale your operations across any city worldwide with ease.',
    icon: Globe,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=800',
  },
  {
    title: 'COMMUNITY POWER',
    description: 'Direct integrations into Discord, Slack, and LinkedIn API to algorithmically identify perfect audience clusters.',
    icon: Users,
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&q=80&w=800',
  },
];

function FeatureCard({ feature, index }) {
  const [hovered, setHovered] = useState(false);
  
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [12, -12]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-12, 12]), { stiffness: 300, damping: 30 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set((e.clientX - rect.left) / rect.width - 0.5);
    mouseY.set((e.clientY - rect.top) / rect.height - 0.5);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
    setHovered(false);
  };

  const Icon = feature.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, rotateX: 20 }}
      whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.6, delay: index * 0.1, type: 'spring', damping: 20 }}
      style={{ perspective: '1200px', cursor: 'crosshair' }}
    >
      <motion.div
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={handleMouseLeave}
        animate={{ scale: hovered ? 1.05 : 1 }}
        style={{
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d',
          position: 'relative',
          height: '400px',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: hovered ? '0 0 40px rgba(0,240,255,0.3)' : '0 20px 40px rgba(0,0,0,0.5)',
        }}
        className="clip-diagonal"
      >
        {/* Deep background image layer */}
        <div style={{
          position: 'absolute',
          inset: '-20px', // slight negative inset to prevent edge clipping on rotation
          background: `url(${feature.image}) center/cover`,
          filter: hovered ? 'grayscale(0%) sepia(20%) hue-rotate(180deg) brightness(0.6)' : 'grayscale(100%) brightness(0.3)',
          transition: 'filter 0.5s ease',
          transform: `translateZ(${hovered ? '-20px' : '0px'}) scale(${hovered ? 1.1 : 1})`,
        }} />

        {/* Glow and darkening overlay */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: hovered 
            ? 'linear-gradient(to top, rgba(2,2,5,1) 0%, rgba(0,240,255,0.1) 100%)' 
            : 'linear-gradient(to top, rgba(2,2,5,0.95) 0%, rgba(2,2,5,0.4) 100%)',
          border: hovered ? '2px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.05)',
          transition: 'all 0.3s ease',
        }} />

        {/* Content Layer (pops out in 3D) */}
        <div style={{
          position: 'absolute',
          inset: 0,
          padding: '32px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          transform: 'translateZ(60px)',
          pointerEvents: 'none'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: hovered ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '20px',
            boxShadow: hovered ? '0 0 20px rgba(0,240,255,0.5)' : 'none',
            transition: 'all 0.3s'
          }}>
            <Icon size={24} color={hovered ? '#000' : 'var(--accent-cyan)'} />
          </div>

          <h3 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '24px',
            fontWeight: 800,
            letterSpacing: '0.05em',
            color: '#fff',
            textShadow: hovered ? '0 0 10px rgba(0,240,255,0.5)' : 'none',
            marginBottom: '12px',
            textTransform: 'uppercase'
          }}>
            {feature.title}
          </h3>

          <p style={{
            fontFamily: 'var(--font-main)',
            fontSize: '15px',
            lineHeight: 1.6,
            color: 'rgba(255,255,255,0.6)',
          }}>
            {feature.description}
          </p>
        </div>

      </motion.div>
    </motion.div>
  );
}

export default function FeaturesSection() {
  return (
    <section id="features" style={{ padding: '160px 0', position: 'relative', zIndex: 10 }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 40px' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '80px' }}>
          <span style={{ 
            fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)', 
            letterSpacing: '0.2em', textTransform: 'uppercase', display: 'block', marginBottom: '16px' 
          }}>
            CAPABILITIES
          </span>
          <h2 className="text-glow-cyan" style={{ 
            fontSize: 'clamp(32px, 5vw, 56px)', fontWeight: 900, 
            fontFamily: 'var(--font-display)', letterSpacing: '0.05em' 
          }}>
            SYSTEM ARCHITECTURE
          </h2>
        </div>

        {/* 3D Features Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '32px',
          perspective: '1500px'
        }}>
          {features.map((feature, i) => (
            <FeatureCard key={feature.title} feature={feature} index={i} />
          ))}
        </div>

      </div>
    </section>
  );
}
