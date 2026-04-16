'use client';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Users, Rocket } from 'lucide-react';

export default function EventPrompt({ onLaunch }) {
  const [eventType, setEventType] = useState('');
  const [city, setCity] = useState('');
  const [attendees, setAttendees] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [isLaunching, setIsLaunching] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!eventType || !city || !attendees) return;
    
    setIsLaunching(true);
    setTimeout(() => {
      onLaunch({ eventType, city, attendees });
      setIsLaunching(false);
      setEventType('');
      setCity('');
      setAttendees('');
    }, 800);
  };

  return (
    <section id="prompt" style={{ padding: '160px 0', position: 'relative', zIndex: 20 }}>
      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '0 24px' }}>
        
        {/* Header - Centered */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <motion.span 
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            style={{ 
              fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)', 
              letterSpacing: '0.2em', textTransform: 'uppercase', display: 'block', marginBottom: '16px' 
            }}
          >
            INITIALIZE SEQUENCE
          </motion.span>
          <motion.h2 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-glow-cyan" 
            style={{ 
              fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 900, 
              fontFamily: 'var(--font-display)', letterSpacing: '0.05em', marginBottom: '12px'
            }}
          >
            DEFINE PARAMETERS
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            style={{ fontSize: '15px', color: 'rgba(255,255,255,0.5)', fontFamily: 'var(--font-main)' }}
          >
            Enter your event type, target city, and expected audience size. The neural network will handle the rest.
          </motion.p>
        </div>

        {/* Minimal Search Bar */}
        <motion.form 
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, type: 'spring', damping: 25 }}
          onSubmit={handleSubmit}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="clip-diagonal"
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            background: 'rgba(2,2,5,0.8)',
            border: `1px solid ${isFocused ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.1)'}`,
            backdropFilter: 'blur(12px)',
            transition: 'all 0.3s ease',
            padding: '8px',
            boxShadow: isFocused ? '0 0 30px rgba(0,240,255,0.2)' : '0 20px 40px rgba(0,0,0,0.5)',
          }}
        >
          {/* Edge Glow on focus */}
          <div style={{
            position: 'absolute',
            inset: 0,
            background: isFocused ? 'var(--accent-cyan-dim)' : 'transparent',
            pointerEvents: 'none',
            transition: 'all 0.3s'
          }} />

          {/* Event Type Input */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px', padding: '0 16px', borderRight: '1px solid rgba(255,255,255,0.1)' }}>
            <Rocket size={18} color={isFocused ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.3)'} style={{ transition: 'color 0.3s' }} />
            <input 
              required
              type="text"
              placeholder="Event Type (e.g. Music, Tech)"
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#fff',
                fontSize: '15px',
                fontFamily: 'var(--font-main)',
                fontWeight: 600,
                letterSpacing: '0.05em'
              }}
            />
          </div>

          {/* City Input */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px', padding: '0 16px', borderRight: '1px solid rgba(255,255,255,0.1)' }}>
            <MapPin size={18} color={isFocused ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.3)'} style={{ transition: 'color 0.3s' }} />
            <input 
              required
              type="text"
              placeholder="City (e.g., Tokyo)"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#fff',
                fontSize: '15px',
                fontFamily: 'var(--font-main)',
                fontWeight: 600,
                letterSpacing: '0.05em'
              }}
            />
          </div>

          {/* Attendees Input */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '8px', padding: '0 16px' }}>
            <Users size={18} color={isFocused ? 'var(--accent-cyan)' : 'rgba(255,255,255,0.3)'} style={{ transition: 'color 0.3s' }} />
            <input 
              required
              type="number"
              placeholder="Attendees"
              value={attendees}
              onChange={(e) => setAttendees(e.target.value)}
              style={{
                width: '100%',
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: '#fff',
                fontSize: '15px',
                fontFamily: 'var(--font-main)',
                fontWeight: 600,
                letterSpacing: '0.05em'
              }}
            />
          </div>

          {/* Launch Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLaunching || !eventType || !city || !attendees}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'var(--accent-cyan)',
              color: '#000',
              border: 'none',
              height: '52px',
              padding: '0 28px',
              fontFamily: 'var(--font-display)',
              fontWeight: 800,
              fontSize: '15px',
              letterSpacing: '0.1em',
              cursor: (isLaunching || !eventType || !city || !attendees) ? 'not-allowed' : 'pointer',
              opacity: (isLaunching || !eventType || !city || !attendees) ? 0.7 : 1,
              transition: 'all 0.2s',
            }}
            className="clip-diagonal"
          >
            {isLaunching ? (
              <span style={{ animation: 'pulse 1s infinite' }}>...</span>
            ) : (
              <>EXECUTE</>
            )}
          </motion.button>
        </motion.form>
      </div>
    </section>
  );
}
