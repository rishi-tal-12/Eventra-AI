'use client';

const links = {
  Product: ['Features', 'Agents', 'Pricing', 'API'],
  Company: ['About', 'Blog', 'Careers', 'Press'],
  Resources: ['Documentation', 'Help Center', 'Community', 'Status'],
  Legal: ['Privacy', 'Terms', 'Security', 'Cookies'],
};

export default function Footer() {
  return (
    <footer
      style={{
        position: 'relative',
        padding: '0 40px 0',
      }}
    >
      {/* Main footer container with border */}
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          borderTop: '1px solid rgba(0, 240, 255, 0.08)',
          padding: '56px 0 0',
        }}
      >
        {/* Footer grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1.4fr repeat(4, 1fr)',
            gap: '40px',
            paddingBottom: '48px',
          }}
        >
          {/* Brand column */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <div
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '8px',
                  background: 'rgba(0, 240, 255, 0.06)',
                  border: '1px solid rgba(0, 240, 255, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path d="M4 5h16M4 12h11M4 19h16" stroke="#00f0ff" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="18" cy="12" r="2" fill="#00f0ff" opacity="0.7" />
                </svg>
              </div>
              <span style={{ fontSize: '15px', fontWeight: 700, fontFamily: 'var(--font-display)', letterSpacing: '0.05em' }}>
                <span style={{ color: '#00f0ff' }}>EVENTRA</span>
                <span style={{ color: 'rgba(255,255,255,0.2)' }}>-</span>
                <span style={{ color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>AI</span>
              </span>
            </div>
            <p style={{
              fontSize: '13px',
              color: 'rgba(255,255,255,0.3)',
              lineHeight: 1.7,
              maxWidth: '240px',
            }}>
              AI-powered event orchestration platform. 8 agents, one perfect event.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(links).map(([category, items]) => (
            <div key={category}>
              <h4
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'rgba(255,255,255,0.5)',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  marginBottom: '16px',
                  fontFamily: 'var(--font-main)',
                }}
              >
                {category}
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {items.map(item => (
                  <li key={item}>
                    <a
                      href="#"
                      style={{
                        fontSize: '13px',
                        color: 'rgba(255,255,255,0.25)',
                        textDecoration: 'none',
                        transition: 'color 0.2s',
                        fontFamily: 'var(--font-main)',
                      }}
                      onMouseEnter={(e) => e.target.style.color = 'rgba(0, 240, 255, 0.7)'}
                      onMouseLeave={(e) => e.target.style.color = 'rgba(255,255,255,0.25)'}
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          style={{
            borderTop: '1px solid rgba(255,255,255,0.04)',
            padding: '20px 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-main)' }}>
            © 2026 Eventra-AI. All rights reserved.
          </p>
          <div style={{ display: 'flex', gap: '20px' }}>
            {['Twitter', 'Discord', 'GitHub', 'LinkedIn'].map(social => (
              <a
                key={social}
                href="#"
                style={{
                  fontSize: '12px',
                  color: 'rgba(255,255,255,0.2)',
                  textDecoration: 'none',
                  fontFamily: 'var(--font-main)',
                  transition: 'color 0.2s',
                }}
                onMouseEnter={(e) => e.target.style.color = 'rgba(0, 240, 255, 0.7)'}
                onMouseLeave={(e) => e.target.style.color = 'rgba(255,255,255,0.2)'}
              >
                {social}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
