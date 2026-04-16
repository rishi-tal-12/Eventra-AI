'use client';
import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as random from 'maath/random/dist/maath-random.esm';

function StarField(props) {
  const ref = useRef();
  // Generate 8000 particles within a sphere
  const sphere = useMemo(() => {
    // using Float32Array to hold x,y,z coordinates
    const positions = new Float32Array(8000 * 3);
    random.inSphere(positions, { radius: 1.5 });
    return positions;
  }, []);

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10;
      ref.current.rotation.y -= delta / 15;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
        <PointMaterial
          transparent
          color="#00f0ff"
          size={0.003}
          sizeAttenuation={true}
          depthWrite={false}
          blending={2} // Additive blending for that glowing dense look
        />
      </Points>
    </group>
  );
}

function StarFieldOrange(props) {
  const ref = useRef();
  const sphere = useMemo(() => {
    // Reduced density drastically from 4000 to 600
    const positions = new Float32Array(600 * 3);
    random.inSphere(positions, { radius: 1.2 });
    // Offset the orange cluster to look like a separate nebula/galaxy
    for(let i=0; i<positions.length; i+=3) {
      positions[i] += 0.5; // shift x
      positions[i+1] -= 0.2; // shift y
    }
    return positions;
  }, []);

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 12;
      ref.current.rotation.y -= delta / 18;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 6]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
        <PointMaterial
          transparent
          color="#f59e0b"
          size={0.003} // Slightly smaller
          sizeAttenuation={true}
          depthWrite={false}
          blending={2}
        />
      </Points>
    </group>
  );
}

export default function ThreeGalaxy() {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: -1, background: '#020205', overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 0, 1] }}>
        <StarField />
        <StarFieldOrange />
      </Canvas>
      {/* Vignette overlay for depth */}
      <div 
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle at center, transparent 0%, #020205 100%)',
          pointerEvents: 'none'
        }}
      />
    </div>
  );
}
