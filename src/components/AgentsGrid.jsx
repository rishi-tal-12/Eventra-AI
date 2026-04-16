'use client';
import { useRef, useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const agents = [
  {
    id: '01',
    name: 'SPONSOR',
    role: 'INTELLIGENCE',
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800',
  },
  {
    id: '02',
    name: 'SPEAKER',
    role: 'DISCOVERY',
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&q=80&w=800',
  },
  {
    id: '03',
    name: 'EXHIBITOR',
    role: 'CLUSTERING',
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1510511459019-5efa7ae5ca97?auto=format&fit=crop&q=80&w=800',
  },
  {
    id: '04',
    name: 'VENUE',
    role: 'MATCHING',
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&q=80&w=800',
  },
  {
    id: '05',
    name: 'FINANCIAL',
    role: 'MODELING',
    color: '#00f0ff',
    image: 'https://images.unsplash.com/photo-1639322537504-6427a16b0a28?auto=format&fit=crop&q=80&w=800',
  },
];

export default function AgentsGrid() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  // Create a wavy dotted path line behind the cards
  const pathLength = useTransform(scrollYProgress, [0.2, 0.8], [0, 1]);

  return (
    <section
      id="agents"
      ref={containerRef}
      style={{
        position: 'relative',
        minHeight: '120vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '0 40px',
        overflow: 'hidden',
        zIndex: 10,
      }}
    >
      <div style={{ maxWidth: '1400px', margin: '0 auto', width: '100%', position: 'relative' }}>
        
        {/* Sci-fi Header */}
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: '20px',
          marginBottom: '80px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          paddingBottom: '10px'
        }}>
          <h2 style={{
            fontSize: 'clamp(40px, 5vw, 64px)',
            fontWeight: 800,
            lineHeight: 0.9,
            color: '#fff',
            textShadow: '0 0 20px rgba(0, 240, 255, 0.3)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <span style={{ color: 'var(--accent-cyan)' }}>AI</span>
            AGENTS
          </h2>
          <span style={{
            marginLeft: 'auto',
            fontFamily: 'var(--font-main)',
            fontSize: '14px',
            color: 'rgba(255,255,255,0.4)',
            letterSpacing: '0.2em'
          }}>
            EVENTRA_AI
          </span>
        </div>

        {/* 3D Slanted Carousel */}
        <div style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '20px',
          perspective: '1500px',
          height: '500px',
        }}>
          
          {/* Animated Dotted Background Path (SVG) */}
          <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: -1 }}>
            <motion.path
              d="M -100 250 Q 200 100, 500 250 T 1100 250 T 1600 250"
              fill="transparent"
              stroke="#00f0ff"
              strokeWidth="2"
              strokeDasharray="4 8"
              opacity="0.5"
              style={{ pathLength }}
            />
          </svg>

          {agents.map((agent, i) => (
            <SlantedCard key={agent.id} agent={agent} index={i} total={agents.length} />
          ))}

        </div>
      </div>
    </section>
  );
}

function SlantedCard({ agent, index, total }) {
  const [hover, setHover] = useState(false);

  // Compute staggered rotation and translation for a curved array look
  const center = (total - 1) / 2;
  const offset = index - center;
  
  // Rotate slightly around Y axis, push back inner cards, slope Z axis
  const rotateY = offset * -8; 
  const translateY = Math.abs(offset) * 20;
  const translateZ = Math.abs(offset) * -50;
  const rotateZ = hover ? 0 : -3;

  return (
    <motion.div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      animate={{
        rotateY: hover ? 0 : rotateY,
        translateY: hover ? -20 : translateY,
        translateZ: hover ? 50 : translateZ,
        rotateZ: rotateZ,
        scale: hover ? 1.05 : 1
      }}
      transition={{
        type: 'spring',
        stiffness: 250,
        damping: 30,
        mass: 1.2
      }}
      style={{
        transformStyle: 'preserve-3d',
        position: 'relative',
        height: '420px',
        width: '280px',
        cursor: 'pointer',
        zIndex: hover ? 100 : 10 - Math.abs(offset),
      }}
    >
      {/* The visible slanted card */}
      <div 
        className="clip-diagonal"
        style={{
          position: 'absolute',
          inset: 0,
          background: `url(${agent.image}) center/cover no-repeat`,
          border: '2px solid rgba(0, 240, 255, 0.1)',
          transition: 'all 0.4s ease',
          filter: hover ? 'grayscale(0%) sepia(20%) hue-rotate(180deg) brightness(1.2)' : 'grayscale(100%) opacity(0.7)',
          boxShadow: hover ? '0 0 30px rgba(0,240,255,0.4), inset 0 0 40px rgba(0,240,255,0.2)' : 'none',
        }}
      >
        {/* Glow overlay */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: hover 
            ? 'linear-gradient(to top, rgba(0,240,255,0.8) 0%, transparent 60%)' 
            : 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 50%)',
          transition: 'all 0.4s ease'
        }} />

        {/* Content Wrapper pushing off the card in 3D */}
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          right: '20px',
          transform: hover ? 'translateZ(40px)' : 'translateZ(0px)',
          transition: 'transform 0.4s ease',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center'
        }}>
          <span style={{
            fontFamily: 'var(--font-main)',
            fontSize: '11px',
            color: hover ? '#000' : 'var(--accent-cyan)',
            background: hover ? 'var(--accent-cyan)' : 'transparent',
            padding: '2px 8px',
            borderRadius: '4px',
            letterSpacing: '0.2em',
            marginBottom: '4px',
            transition: 'all 0.3s ease'
          }}>
            {agent.role}
          </span>
          <h3 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '24px',
            fontWeight: 800,
            letterSpacing: '0.05em',
            color: '#fff',
            textShadow: hover ? '0 0 10px rgba(255,255,255,0.5)' : 'none',
            margin: 0
          }}>
            {agent.name}
          </h3>
        </div>
      </div>
    </motion.div>
  );
}
