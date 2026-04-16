'use client';
import { useState } from 'react';
import MouseGlow from '@/components/MouseGlow';
import ThreeGalaxy from '@/components/ThreeGalaxy';
import FloatingNav from '@/components/FloatingNav';
import HeroSection from '@/components/HeroSection';
import AgentsGrid from '@/components/AgentsGrid';
import EventPrompt from '@/components/EventPrompt';
import WorkflowSection from '@/components/WorkflowSection';
import FeaturesSection from '@/components/FeaturesSection';

import Footer from '@/components/Footer';

export default function Home() {
  const [workflowActive, setWorkflowActive] = useState(false);
  const [eventData, setEventData] = useState(null);

  const handleLaunch = (data: any) => {
    setEventData(data);
    setWorkflowActive(true);
    // Scroll to workflow section
    setTimeout(() => {
      document.getElementById('workflow')?.scrollIntoView({ behavior: 'smooth' });
    }, 300);
  };

  return (
    <>
      {/* Global immersive background */}
      <ThreeGalaxy />
      <FloatingNav />

      {/* Main content */}
      <main>
        <HeroSection />
        <AgentsGrid />
        <EventPrompt onLaunch={handleLaunch} />
        <WorkflowSection isActive={workflowActive} eventData={eventData} />
        <FeaturesSection />

        <Footer />
      </main>
    </>
  );
}
