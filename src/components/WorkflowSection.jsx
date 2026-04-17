'use client';
import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView, useMotionValue, useSpring, useTransform } from 'framer-motion';
import {
  Handshake, Mic2, Store, MapPin, TrendingUp, Megaphone, CalendarClock, PiggyBank,
  CheckCircle2, Loader2, ArrowRight, Mail, Phone, ExternalLink, X,
  Building2, Globe, TrendingDown, Award, Briefcase, DollarSign
} from 'lucide-react';

const agentDefs = [
  { id: 1, name: 'Sponsor', icon: Handshake, color: '#00f0ff' },
  { id: 2, name: 'Speaker', icon: Mic2, color: '#00f0ff' },
  { id: 3, name: 'Exhibitor', icon: Store, color: '#00f0ff' },
  { id: 4, name: 'Venue', icon: MapPin, color: '#00f0ff' },
  { id: 5, name: 'Pricing', icon: TrendingUp, color: '#00f0ff' },
  { id: 6, name: 'GTM', icon: Megaphone, color: '#00f0ff' },
  { id: 7, name: 'Ops', icon: CalendarClock, color: '#00f0ff' },
  { id: 8, name: 'Finance', icon: PiggyBank, color: '#00f0ff' },
];

const mockResults = {
  0: {
    title: 'Recommended Sponsors',
    items: [
      { name: 'Stripe', role: 'Fintech · Series D+', match: 94, icon: Building2, metric: '$50K–$100K', metricLabel: 'Est. Budget', image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800' },
      { name: 'Vercel', role: 'Developer Platform', match: 91, icon: Globe, metric: '$25K–$50K', metricLabel: 'Est. Budget', image: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=800' },
      { name: 'Datadog', role: 'Observability · Public', match: 87, icon: TrendingDown, metric: '$75K', metricLabel: 'Est. Budget', image: 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  1: {
    title: 'Matched Speakers',
    items: [
      { name: 'Dr. Sarah Chen', role: 'AI Research Lead', match: 96, icon: Award, metric: '120K', metricLabel: 'Followers', image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=800' },
      { name: 'Raj Patel', role: 'CTO · TechUnicorn', match: 91, icon: Award, metric: '85K', metricLabel: 'Followers', image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=800' },
      { name: 'Maya Johnson', role: 'VP Eng · Netflix', match: 88, icon: Award, metric: '210K', metricLabel: 'Followers', image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  2: {
    title: 'Potential Exhibitors',
    items: [
      { name: 'LaunchPad AI', role: 'Startup · AI/ML Tools', match: 92, icon: Building2, metric: 'Startup', metricLabel: 'Category', image: 'https://images.unsplash.com/photo-1481481312836-294b5bf5f30c?auto=format&fit=crop&q=80&w=800' },
      { name: 'ToolStack Pro', role: 'Dev Tools · B2B SaaS', match: 87, icon: Briefcase, metric: 'Enterprise', metricLabel: 'Category', image: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&q=80&w=800' },
      { name: 'CloudForge', role: 'Infrastructure · Cloud', match: 83, icon: Globe, metric: 'Enterprise', metricLabel: 'Category', image: 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  3: {
    title: 'Venue Options',
    items: [
      { name: 'Grand Tech Arena', role: 'Convention Center', match: 95, icon: Building2, metric: '5,000 cap', metricLabel: '$12K/day', image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&q=80&w=800' },
      { name: 'Innovation Hub', role: 'Co-working Campus', match: 89, icon: Building2, metric: '2,000 cap', metricLabel: '$6K/day', image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800' },
      { name: 'Skyview Centre', role: 'Expo Hall', match: 84, icon: Building2, metric: '8,000 cap', metricLabel: '$18K/day', image: 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  4: {
    title: 'Pricing Analysis',
    items: [
      { name: 'Early Bird Tier', role: 'First 200 tickets', match: 97, icon: DollarSign, metric: '₹2,999', metricLabel: 'Suggested', image: 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?auto=format&fit=crop&q=80&w=800' },
      { name: 'Standard Tier', role: 'General admission', match: 94, icon: DollarSign, metric: '₹4,499', metricLabel: 'Suggested', image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&q=80&w=800' },
      { name: 'VIP Access', role: 'Networking dinner', match: 90, icon: DollarSign, metric: '₹9,999', metricLabel: 'Suggested', image: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  5: {
    title: 'Distribution Channels',
    items: [
      { name: 'Tech Twitter / X', role: 'Primary channel', match: 95, icon: Globe, metric: '2.4M', metricLabel: 'Est. Reach', image: 'https://images.unsplash.com/photo-1611605698335-8b1569810432?auto=format&fit=crop&q=80&w=800' },
      { name: 'Discord Servers', role: '12 relevant servers', match: 89, icon: Megaphone, metric: '180K', metricLabel: 'Members', image: 'https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?auto=format&fit=crop&q=80&w=800' },
      { name: 'LinkedIn Groups', role: '8 professional groups', match: 86, icon: Briefcase, metric: '340K', metricLabel: 'Members', image: 'https://images.unsplash.com/photo-1611926653458-09294b3142bf?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  6: {
    title: 'Schedule Draft',
    items: [
      { name: 'Opening Keynote', role: '9:00 AM · Main Hall', match: 100, icon: CalendarClock, metric: '60 min', metricLabel: 'Duration', image: 'https://images.unsplash.com/photo-1475721028070-2051152a5ca4?auto=format&fit=crop&q=80&w=800' },
      { name: 'Panel: Future of AI', role: '10:30 AM · Stage A', match: 98, icon: CalendarClock, metric: '60 min', metricLabel: 'Duration', image: 'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?auto=format&fit=crop&q=80&w=800' },
      { name: 'Networking Lunch', role: '12:00 PM · Atrium', match: 95, icon: CalendarClock, metric: '90 min', metricLabel: 'Duration', image: 'https://images.unsplash.com/photo-1528605248644-14dd04022da1?auto=format&fit=crop&q=80&w=800' },
    ]
  },
  7: {
    title: 'Financial Projections',
    items: [
      { name: 'Projected Revenue', role: '1,200 attendees', match: 92, icon: TrendingUp, metric: '₹54L', metricLabel: 'Estimated', image: 'https://images.unsplash.com/photo-1543286386-713bdd548da4?auto=format&fit=crop&q=80&w=800' },
      { name: 'Total Costs', role: 'Venue + F&B + Ops', match: 88, icon: TrendingDown, metric: '₹32L', metricLabel: 'Estimated', image: 'https://images.unsplash.com/photo-1579621970588-a35d0e7ab9b6?auto=format&fit=crop&q=80&w=800' },
      { name: 'Net Margin', role: 'Break-even at 680 tickets', match: 96, icon: DollarSign, metric: '40.7%', metricLabel: 'Projected', image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800' },
    ]
  },
};

function ResultCard({ item, selected, onSelect }) {
  const [hovered, setHovered] = useState(false);

  // 3D Tilt properties
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), { stiffness: 300, damping: 30 });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), { stiffness: 300, damping: 30 });

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

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8, rotateX: 15 }}
      animate={{ opacity: 1, scale: 1, rotateX: 0 }}
      layout
      transition={{ type: 'spring', damping: 20, stiffness: 100 }}
      onClick={onSelect}
      style={{ perspective: '1200px', cursor: 'pointer', flex: '1 1 300px', maxWidth: '400px' }}
    >
      <motion.div
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={handleMouseLeave}
        animate={{ scale: selected ? 1.02 : hovered ? 1.05 : 1 }}
        style={{
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d',
          position: 'relative',
          height: '400px',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: selected 
            ? '0 0 30px rgba(0,240,255,0.4), inset 0 0 40px rgba(0,240,255,0.2)' 
            : hovered ? '0 30px 40px rgba(0,0,0,0.5)' : '0 20px 25px rgba(0,0,0,0.4)',
        }}
        className="clip-diagonal"
      >
        {/* Background Image */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: `url(${item.image}) center/cover`,
          filter: selected ? 'grayscale(0%) sepia(20%) hue-rotate(180deg) brightness(0.8)' : hovered ? 'grayscale(10%) brightness(0.7)' : 'grayscale(100%) brightness(0.4)',
          transition: 'all 0.4s ease',
        }} />

        {/* Selected Border / Overlay */}
        <div style={{
          position: 'absolute',
          inset: 0,
          border: selected ? '2px solid var(--accent-cyan)' : '1px solid rgba(255,255,255,0.05)',
          background: selected ? 'var(--accent-cyan-dim)' : 'transparent',
          transition: 'all 0.3s ease',
        }} />

        {/* Gradient Overlay for text readability */}
        <div style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(2,2,5,0.95) 0%, rgba(2,2,5,0.4) 50%, transparent 100%)',
          pointerEvents: 'none'
        }} />

        {/* Match Badge */}
        <div style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(10px)',
          padding: '6px 12px',
          borderRadius: '8px',
          border: '1px solid rgba(0, 240, 255, 0.4)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          transform: 'translateZ(30px)',
        }}>
          <span style={{ color: 'var(--accent-cyan)', fontSize: '14px', fontWeight: 800, fontFamily: 'var(--font-display)' }}>{item.match}%</span>
          <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '1px' }}>MATCH</span>
        </div>

        {/* Selection Checkmark */}
        {selected && (
          <div style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            background: 'var(--accent-cyan)',
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: 'translateZ(40px)',
            boxShadow: '0 0 20px rgba(0,240,255,0.5)',
          }}>
            <CheckCircle2 color="#000" size={18} />
          </div>
        )}

        {/* Card Content (pops out in 3D) */}
        <div style={{
          position: 'absolute',
          bottom: '30px',
          left: '24px',
          right: '24px',
          transform: 'translateZ(50px)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <span style={{
            fontFamily: 'var(--font-main)',
            fontSize: '12px',
            color: 'var(--accent-cyan)',
            textTransform: 'uppercase',
            letterSpacing: '0.15em',
            marginBottom: '4px'
          }}>{item.role}</span>
          
          <h3 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '28px',
            fontWeight: 800,
            textShadow: '0 0 10px rgba(0,0,0,0.8)',
            marginBottom: '16px'
          }}>{item.name}</h3>

          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: '8px',
            borderTop: '1px solid rgba(255,255,255,0.1)',
            paddingTop: '16px'
          }}>
            <span style={{ fontSize: '24px', fontFamily: 'var(--font-display)', fontWeight: 700, color: '#fff' }}>{item.metric}</span>
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '1px' }}>{item.metricLabel}</span>
          </div>
        </div>

      </motion.div>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers: extract contact info + build objective
// ─────────────────────────────────────────────────────────────────────────────

const BACKUP_PHONE = '+919810706119';
const BACKUP_EMAIL = 'contact.sid.chopra@gmail.com';

/** Map agent index → the /api/select/* endpoint field names */
const SELECTION_ENDPOINTS = {
  0: { path: '/api/select/sponsors',   bodyKey: 'selected_sponsors' },
  1: { path: '/api/select/speakers',   bodyKey: 'selected_speakers' },
  2: { path: '/api/select/exhibitors', bodyKey: 'selected_exhibitors' },
  3: { path: '/api/select/venue',      bodyKey: 'selected_venue' },
};

/** Try to pull an email from an item object */
function extractEmail(item) {
  if (!item) return null;
  for (const key of ['email', 'contact_email', 'Email', 'e_mail']) {
    if (item[key] && typeof item[key] === 'string' && item[key].includes('@')) return item[key];
  }
  return null;
}

/** Try to pull a phone number from an item object */
function extractPhone(item) {
  if (!item) return null;
  for (const key of ['phone', 'mobile', 'phone_number', 'contact_phone', 'Phone', 'mobile_number']) {
    if (item[key] && typeof item[key] === 'string') return item[key];
  }
  return null;
}

/** Agent-index → human-readable role label */
const AGENT_ROLE_LABELS = {
  0: 'sponsorship',
  1: 'speaker / artist booking',
  2: 'exhibitor participation',
  3: 'venue booking',
  4: 'pricing',
  5: 'marketing & community',
  6: 'scheduling',
  7: 'financial planning',
};

/** Build a context-rich objective string for email / call from the frontend */
function buildObjective(agentIndex, selectedItemObjects, eventData) {
  const roleLabel = AGENT_ROLE_LABELS[agentIndex] || 'collaboration';
  const names = selectedItemObjects.map(i => i.name).join(', ');

  let eventContext = '';
  if (eventData) {
    eventContext = ` for a ${eventData.eventType || ''} event in ${eventData.city || ''} expecting ${eventData.attendees || ''} attendees`;
  }

  return `Reach out to ${names} regarding a ${roleLabel} opportunity${eventContext}. Introduce Eventra, express interest in partnership, and request availability and pricing details.`;
}

function ActionModal({ isOpen, onClose, count, agentName, selectedItemObjects, sessionId, currentAgent, eventData }) {
  const [actionState, setActionState] = useState('idle'); // idle | submitting | emailing | calling | done | error
  const [statusMsg, setStatusMsg] = useState('');

  if (!isOpen) return null;

  // ── submit selections to backend ──────────────────────────────────────
  const submitSelections = async () => {
    const endpoint = SELECTION_ENDPOINTS[currentAgent];
    if (!endpoint || !sessionId) return true; // nothing to submit, treat as ok
    try {
      const res = await fetch(`http://localhost:5000${endpoint.path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          [endpoint.bodyKey]: selectedItemObjects,
        }),
      });
      if (!res.ok) throw new Error(`Selection API returned ${res.status}`);
      return true;
    } catch (err) {
      console.error('Failed to submit selections:', err);
      return false;
    }
  };

  // ── email handler ─────────────────────────────────────────────────────
  const handleEmail = async () => {
    setActionState('submitting');
    setStatusMsg('Submitting selections…');

    const ok = await submitSelections();
    if (!ok) {
      setActionState('error');
      setStatusMsg('Failed to submit selections. Please retry.');
      return;
    }

    setActionState('emailing');
    setStatusMsg('Transmitting proposals…');

    const objective = buildObjective(currentAgent, selectedItemObjects, eventData);
    let successCount = 0;

    for (const item of selectedItemObjects) {
      const recipientEmail = extractEmail(item) || BACKUP_EMAIL;
      try {
        const res = await fetch('http://localhost:5000/api/email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            recipient_email: recipientEmail,
            objective,
          }),
        });
        const data = await res.json();
        if (res.ok && data.status !== 'failure') {
          successCount++;
          console.log(`Email sent to ${recipientEmail} for ${item.name}`, data);
        } else {
          console.warn(`Email failed for ${item.name}:`, data);
        }
      } catch (err) {
        console.error(`Email error for ${item.name}:`, err);
      }
    }

    setActionState('done');
    setStatusMsg(`${successCount}/${selectedItemObjects.length} proposals transmitted successfully.`);
  };

  // ── call handler ──────────────────────────────────────────────────────
  const handleCall = async () => {
    setActionState('submitting');
    setStatusMsg('Submitting selections…');

    const ok = await submitSelections();
    if (!ok) {
      setActionState('error');
      setStatusMsg('Failed to submit selections. Please retry.');
      return;
    }

    setActionState('calling');
    setStatusMsg('Establishing commlinks…');

    const objective = buildObjective(currentAgent, selectedItemObjects, eventData);
    let successCount = 0;

    for (const item of selectedItemObjects) {
      const phoneNumber = extractPhone(item) || BACKUP_PHONE;
      try {
        const res = await fetch('http://localhost:5000/api/call', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            phone_number: phoneNumber,
            input_string: objective,
          }),
        });
        const data = await res.json();
        if (res.ok && !data.error) {
          successCount++;
          console.log(`Call initiated to ${phoneNumber} for ${item.name}`, data);
        } else {
          console.warn(`Call failed for ${item.name}:`, data);
        }
      } catch (err) {
        console.error(`Call error for ${item.name}:`, err);
      }
    }

    setActionState('done');
    setStatusMsg(`${successCount}/${selectedItemObjects.length} commlinks established.`);
  };

  const isBusy = ['submitting', 'emailing', 'calling'].includes(actionState);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={isBusy ? undefined : onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(2,2,5,0.8)',
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          zIndex: 10000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
        }}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0, y: 30 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 30 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          onClick={(e) => e.stopPropagation()}
          className="clip-diagonal"
          style={{
            background: 'linear-gradient(135deg, rgba(16,24,39,0.9), rgba(2,2,5,0.9))',
            border: '1px solid var(--accent-cyan)',
            padding: '40px',
            maxWidth: '500px',
            width: '100%',
            position: 'relative',
            boxShadow: '0 0 60px rgba(0,240,255,0.15)'
          }}
        >
          <button
            onClick={isBusy ? undefined : onClose}
            disabled={isBusy}
            style={{
              position: 'absolute', top: '20px', right: '20px',
              background: 'rgba(0,240,255,0.1)', border: '1px solid var(--accent-cyan)', color: 'var(--accent-cyan)',
              cursor: isBusy ? 'not-allowed' : 'pointer', width: '32px', height: '32px', borderRadius: '4px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              opacity: isBusy ? 0.4 : 1,
            }}
          >
            <X size={16} />
          </button>

          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)', letterSpacing: '0.2em', textTransform: 'uppercase', marginBottom: '16px' }}>
            OUTREACH PROTOCOL
          </div>
          <h3 style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-display)', marginBottom: '8px', letterSpacing: '0.05em', color: '#fff' }}>
            ENGAGE {count} TARGETS
          </h3>
          <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', marginBottom: '32px', fontFamily: 'var(--font-main)' }}>
            Initiating connection protocol for selected {agentName.toLowerCase()} matches.
          </p>

          {/* Status Banner */}
          {actionState !== 'idle' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              style={{
                marginBottom: '20px',
                padding: '14px 18px',
                borderRadius: '8px',
                background: actionState === 'error'
                  ? 'rgba(255,60,60,0.12)'
                  : actionState === 'done'
                    ? 'rgba(0,240,255,0.1)'
                    : 'rgba(255,200,0,0.08)',
                border: `1px solid ${actionState === 'error' ? 'rgba(255,60,60,0.4)' : actionState === 'done' ? 'var(--accent-cyan)' : 'rgba(255,200,0,0.3)'}`,
                fontSize: '13px',
                fontFamily: 'var(--font-main)',
                color: actionState === 'error' ? '#ff5e5e' : actionState === 'done' ? 'var(--accent-cyan)' : 'rgba(255,220,100,0.9)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
              }}
            >
              {isBusy && (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                  <Loader2 size={16} />
                </motion.div>
              )}
              {actionState === 'done' && <CheckCircle2 size={16} />}
              {statusMsg}
            </motion.div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <motion.button
              whileHover={isBusy ? {} : { scale: 1.02, x: 8 }}
              whileTap={isBusy ? {} : { scale: 0.98 }}
              className="btn-sci-fi-filled clip-button"
              disabled={isBusy}
              onClick={handleEmail}
              style={{
                display: 'flex', alignItems: 'center', gap: '16px',
                padding: '16px 24px', width: '100%', textAlign: 'left',
                opacity: isBusy ? 0.5 : 1,
                cursor: isBusy ? 'not-allowed' : 'pointer',
              }}
            >
              <Mail size={18} />
              TRANSMIT PROPOSAL (EMAIL)
              <ArrowRight size={16} style={{ marginLeft: 'auto' }} />
            </motion.button>

            <motion.button
              whileHover={isBusy ? {} : { scale: 1.02, x: 8 }}
              whileTap={isBusy ? {} : { scale: 0.98 }}
              className="btn-sci-fi-filled clip-button"
              disabled={isBusy}
              onClick={handleCall}
              style={{
                display: 'flex', alignItems: 'center', gap: '16px',
                padding: '16px 24px', width: '100%', textAlign: 'left',
                opacity: isBusy ? 0.5 : 1,
                cursor: isBusy ? 'not-allowed' : 'pointer',
              }}
            >
              <Phone size={18} />
              ESTABLISH COMMLINK (CALL)
              <ArrowRight size={16} style={{ marginLeft: 'auto' }} />
            </motion.button>

            <motion.button
              whileHover={isBusy ? {} : { scale: 1.02, x: 8 }}
              whileTap={isBusy ? {} : { scale: 0.98 }}
              className="btn-sci-fi-filled clip-button"
              disabled={isBusy}
              style={{
                display: 'flex', alignItems: 'center', gap: '16px',
                padding: '16px 24px', width: '100%', textAlign: 'left',
                opacity: isBusy ? 0.5 : 1,
                cursor: isBusy ? 'not-allowed' : 'pointer',
              }}
            >
              <ExternalLink size={18} />
              GENERATE DOSSIER (PDF)
              <ArrowRight size={16} style={{ marginLeft: 'auto' }} />
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export default function WorkflowSection({ isActive, eventData }) {
  const [currentAgent, setCurrentAgent] = useState(0);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [showActionModal, setShowActionModal] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [pipelineResults, setPipelineResults] = useState(mockResults);
  const [sessionId, setSessionId] = useState(null);
  const [apiResponseData, setApiResponseData] = useState(null);
  const sectionRef = useRef(null);

  useEffect(() => {
    if (isActive && currentAgent === 0 && completedAgents.length === 0) {
      runAgent(0);
    }
  }, [isActive]);

  const runAgent = async (idx) => {
    setCurrentAgent(idx);
    setSelectedItems([]);
    setShowResults(false);

    try {
      if (idx === 0 && eventData) {
        // 1. Initial & Sponsor
        const prompt = `Create a ${eventData.eventType} event in ${eventData.city} for ${eventData.attendees} attendees.`;
        const res = await fetch('http://localhost:5000/api/init_and_sponsor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        
        setSessionId(data.session_id);
        setApiResponseData(data); // Store for console logging

        if (data.sponsors && data.sponsors.length > 0) {
          const sponsorItems = data.sponsors.map((s, i) => ({
            name: s.name || s.company_name || s.company || `Sponsor ${i+1}`,
            role: s.industry || s.reason || 'Sponsorship Match',
            match: s.match_score || Math.floor(Math.random() * 20 + 80),
            icon: Building2, 
            metric: s.budget || 'Custom', 
            metricLabel: 'Budget',
            image: mockResults[0]?.items[i % 3]?.image || 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800'
          }));
          setPipelineResults(prev => ({
            ...prev,
            0: { ...prev[0], items: sponsorItems }
          }));
        }
      } else if (sessionId) {
        let endpoints = [];
        if (idx === 1) endpoints = ['/api/speaker'];
        if (idx === 2) endpoints = ['/api/exhibitor'];
        if (idx === 3) endpoints = ['/api/venue'];
        if (idx === 4) endpoints = ['/api/pricing'];
        if (idx === 5) endpoints = ['/api/community', '/api/instagram'];
        if (idx === 6) endpoints = ['/api/schedule'];

        if (endpoints.length > 0) {
          const results = await Promise.all(
            endpoints.map(ep => fetch(`http://localhost:5000${ep}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ session_id: sessionId })
            }).then(r => r.json()))
          );
          
          const combinedData = Object.assign({}, ...results);
          setApiResponseData(combinedData);

          let itemsData = [];
          let itemsField = 'items';
          let defaultMetricLabel = 'Details';
          let metricField = 'metric';
          
          if (idx === 1) { itemsField = 'speakers_artists'; metricField = 'location'; defaultMetricLabel = 'Location'; }
          if (idx === 2) { itemsField = 'exhibitors'; metricField = 'industry'; defaultMetricLabel = 'Industry'; }
          if (idx === 3) { itemsField = 'venues'; metricField = 'capacity'; defaultMetricLabel = 'Capacity'; }
          // Handle pricing
          if (idx === 4) { itemsField = 'pricing'; }
          // Handle community & instagram combined
          if (idx === 5) { itemsField = 'communities'; }
          if (idx === 6) { itemsField = 'schedule'; }

          if (combinedData[itemsField] && Array.isArray(combinedData[itemsField])) {
            itemsData = combinedData[itemsField].slice(0, 3).map((s, i) => ({
              name: s.name || s.title || s.company_name || s.stage_name || `Result ${i+1}`,
              role: s.role || s.industry || s.description || s.city || 'Processed',
              match: s.match_score || Math.floor(Math.random() * 20 + 80),
              icon: Globe, 
              metric: s[metricField] || s.price || s.budget || 'Custom', 
              metricLabel: defaultMetricLabel,
              image: mockResults[idx]?.items[i % 3]?.image || 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&q=80&w=800'
            }));
            
            if (itemsData.length > 0) {
               setPipelineResults(prev => ({
                 ...prev,
                 [idx]: { ...(prev[idx] || {}), items: itemsData }
               }));
            }
          }
        }
      }
    } catch (err) {
      console.error(`Error running agent index ${idx}:`, err);
    }

    setTimeout(() => setShowResults(true), 1500); // Wait simulated time
  };

  const completeAgent = async () => {
    // Submit selections to backend before advancing
    const endpoint = SELECTION_ENDPOINTS[currentAgent];
    if (endpoint && sessionId && selectedItems.length > 0) {
      const selectedObjs = results?.items?.filter(item => selectedItems.includes(item.name)) || [];
      try {
        await fetch(`http://localhost:5000${endpoint.path}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            [endpoint.bodyKey]: selectedObjs,
          }),
        });
      } catch (err) {
        console.warn('Selection submission failed (non-blocking):', err);
      }
    }

    setCompletedAgents(prev => [...prev, currentAgent]);
    setShowResults(false);
    if (currentAgent < agentDefs.length - 1) {
      setTimeout(() => runAgent(currentAgent + 1), 400);
    }
  };

  const toggleItem = (name) => {
    setSelectedItems(prev => prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name]);
  };

  const getStatus = (idx) => {
    if (completedAgents.includes(idx)) return 'done';
    if (idx === currentAgent && isActive) return 'active';
    return 'pending';
  };

  const active = agentDefs[currentAgent];
  const results = pipelineResults[currentAgent];
  const allDone = completedAgents.length === agentDefs.length;

  // Fully expansive dark section
  return (
    <section id="workflow" ref={sectionRef} style={{ position: 'relative', width: '100vw', marginLeft: 'calc(-50vw + 50%)', padding: '120px 0', minHeight: '100vh', background: 'rgba(2,2,5,0.5)', overflow: 'hidden' }}>
      <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 40px', width: '100%' }}>
        
        {/* Header - Centered */}
        <div style={{ textAlign: 'center', marginBottom: '80px' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)', letterSpacing: '0.2em', textTransform: 'uppercase', display: 'block', marginBottom: '16px' }}>
            SYSTEM PIPELINE
          </span>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', fontWeight: 900, fontFamily: 'var(--font-display)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
            {allDone ? 'PIPELINE COMPLETE' : (
              <>RUNNING <span className="text-glow-cyan" style={{ color: 'var(--accent-cyan)' }}>{active?.name}</span> AGENT</>
            )}
          </h2>
        </div>

        {/* Pipeline progress bar - Centered */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0',
          marginBottom: '80px', flexWrap: 'wrap',
        }}>
          {agentDefs.map((a, i) => {
            const status = getStatus(i);
            const Icon = a.icon;
            return (
              <div key={a.id} style={{ display: 'flex', alignItems: 'center' }}>
                <motion.div
                  animate={{
                    scale: status === 'active' ? 1.2 : 1,
                  }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  style={{
                    width: '56px', height: '56px', borderRadius: '12px',
                    background: status === 'done' ? 'rgba(0,240,255,0.1)' : status === 'active' ? 'rgba(0,240,255,0.15)' : 'rgba(255,255,255,0.02)',
                    border: `1px solid ${status === 'done' ? 'var(--accent-cyan)' : status === 'active' ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    position: 'relative', boxShadow: status === 'active' ? `0 0 30px rgba(0,240,255,0.4)` : 'none',
                    transform: 'rotate(45deg)' // Diamond shape for sci-fi look
                  }}
                >
                  <div style={{ transform: 'rotate(-45deg)' }}>
                    {status === 'done' ? (
                      <CheckCircle2 size={24} color="var(--accent-cyan)" strokeWidth={2} />
                    ) : status === 'active' ? (
                      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}>
                        <Loader2 size={24} color="var(--accent-cyan)" strokeWidth={2} />
                      </motion.div>
                    ) : (
                      <Icon size={20} color="rgba(255,255,255,0.2)" strokeWidth={1.5} />
                    )}
                  </div>
                </motion.div>
                {i < agentDefs.length - 1 && (
                  <div style={{
                    width: '32px', height: '2px',
                    background: completedAgents.includes(i) ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.05)',
                    boxShadow: completedAgents.includes(i) ? '0 0 10px var(--accent-cyan)' : 'none',
                    transition: 'all 0.5s',
                  }} />
                )}
              </div>
            );
          })}
        </div>

        {/* Action / Results Arena */}
        {!allDone && isActive && (
          <AnimatePresence mode="wait">
            <motion.div
              key={currentAgent}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -40 }}
              transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}
            >
              {/* Results Title */}
              {showResults && results && (
                <div style={{ textAlign: 'center', width: '100%', marginBottom: '40px' }}>
                  <h3 style={{ fontSize: '24px', fontWeight: 700, fontFamily: 'var(--font-display)', color: '#fff', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                    {results.title}
                  </h3>
                </div>
              )}

              {/* Advanced 3D Result Cards */}
              {showResults && results && (
                <motion.div
                  initial="hidden"
                  animate="visible"
                  variants={{
                    visible: { transition: { staggerChildren: 0.1 } },
                    hidden: {}
                  }}
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    justifyContent: 'center',
                    gap: '32px',
                    width: '100%',
                    marginBottom: '60px'
                  }}
                >
                  {results.items.map((item) => (
                    <ResultCard
                      key={item.name}
                      item={item}
                      selected={selectedItems.includes(item.name)}
                      onSelect={() => toggleItem(item.name)}
                    />
                  ))}
                </motion.div>
              )}

              {/* Simulated Progress State Elements */}
              {!showResults && (
                <div style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: 'linear' }} style={{ marginBottom: '24px' }}>
                    <div style={{ width: '80px', height: '80px', borderRadius: '50%', border: '2px dashed var(--accent-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Loader2 size={32} color="var(--accent-cyan)" />
                    </div>
                  </motion.div>
                  <div style={{ fontSize: '18px', fontFamily: 'var(--font-display)', color: 'var(--accent-cyan)', letterSpacing: '0.1em' }} className="text-glow-cyan">
                    PROCESSING DEMOGRAPHICS...
                  </div>
                </div>
              )}

              {/* Action Bar (Only shows when results are ready) */}
              {showResults && (
                <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', width: '100%' }}>
                  {selectedItems.length > 0 && (
                    <motion.button
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="btn-sci-fi clip-button"
                      onClick={() => {
                        console.log('Backend Agent Response:', apiResponseData);
                        setShowActionModal(true);
                      }}
                    >
                      ENGAGE TARGETS ({selectedItems.length})
                    </motion.button>
                  )}
                  <motion.button
                    className="btn-sci-fi-filled clip-button"
                    onClick={completeAgent}
                  >
                    CONFIRM & PROCEED <ArrowRight size={18} style={{ marginLeft: '12px' }} />
                  </motion.button>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        )}

        {/* All done */}
        {allDone && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{
              textAlign: 'center',
              padding: '80px 40px',
              background: 'rgba(0,240,255,0.05)',
              border: '1px solid var(--accent-cyan)',
              borderRadius: '24px',
              maxWidth: '800px',
              margin: '0 auto'
            }}
            className="clip-diagonal"
          >
            <CheckCircle2 size={64} color="var(--accent-cyan)" strokeWidth={1.5} style={{ marginBottom: '24px', filter: 'drop-shadow(0 0 20px rgba(0,240,255,0.5))' }} />
            <h3 style={{ fontSize: '36px', fontWeight: 900, fontFamily: 'var(--font-display)', marginBottom: '16px', letterSpacing: '0.05em' }} className="text-glow-cyan">
              ORCHESTRATION COMPLETE
            </h3>
            <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.6)', fontFamily: 'var(--font-main)' }}>
              All agents have successfully executed their routines. The master dossier has been compiled.
            </p>
          </motion.div>
        )}
      </div>

      <ActionModal
        isOpen={showActionModal}
        onClose={() => setShowActionModal(false)}
        count={selectedItems.length}
        agentName={active?.name || ''}
        selectedItemObjects={
          results?.items?.filter(item => selectedItems.includes(item.name)) || []
        }
        sessionId={sessionId}
        currentAgent={currentAgent}
        eventData={eventData}
      />
    </section>
  );
}
