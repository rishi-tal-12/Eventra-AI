import './globals.css';
import { Orbitron, Rajdhani, Space_Grotesk } from 'next/font/google';

const orbitron = Orbitron({ 
  subsets: ['latin'], 
  variable: '--font-display',
  weight: ['400', '500', '600', '700', '800', '900'] 
});

const rajdhani = Rajdhani({ 
  subsets: ['latin'], 
  variable: '--font-main',
  weight: ['300', '400', '500', '600', '700'] 
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-accent',
  weight: ['300', '400', '500', '600', '700']
});

export const metadata = {
  title: 'Eventra-AI — AI Event Orchestration',
  description: 'AI-powered event management platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" style={{ scrollBehavior: 'smooth' }}>
      <body
        className={`${orbitron.variable} ${rajdhani.variable} ${spaceGrotesk.variable}`}
        style={{
          backgroundColor: '#020205',
          fontFamily: 'var(--font-main)',
          color: 'var(--text-primary)',
          overflowX: 'hidden',
          minHeight: '100vh',
        }}
      >
        {children}
      </body>
    </html>
  );
}
