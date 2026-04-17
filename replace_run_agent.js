const fs = require('fs');
const file = 'src/components/WorkflowSection.jsx';
let code = fs.readFileSync(file, 'utf8');

const regex = /const runAgent = async \(idx\) => \{[\s\S]*?setTimeout\(\(\) => setShowResults\(true\), 1500\);\s*\/\/\sWait simulated time\s*\};/;

const newRunAgent = `const runAgent = async (idx) => {
    setCurrentAgent(idx);
    setSelectedItems([]);
    setShowResults(false);

    try {
      if (idx === 0 && eventData) {
        // 1. Initial & Sponsor
        const prompt = \`Create a \${eventData.eventType} event in \${eventData.city} for \${eventData.attendees} attendees.\`;
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
            name: s.name || s.company_name || s.company || \`Sponsor \${i+1}\`,
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
            endpoints.map(ep => fetch(\`http://localhost:5000\${ep}\`, {
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
              name: s.name || s.title || s.company_name || s.stage_name || \`Result \${i+1}\`,
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
      console.error(\`Error running agent index \${idx}:\`, err);
    }

    setTimeout(() => setShowResults(true), 1500); // Wait simulated time
  };`;

if (!regex.test(code)) {
  console.log("Could not find runAgent to replace!");
} else {
  code = code.replace(regex, newRunAgent);
  fs.writeFileSync(file, code);
  console.log("Successfully updated runAgent!");
}
