"use client";

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { 
  PARTICLE_CONFIG, 
  PARTICLE_COLORS, 
  AMBIENT_STATE_CONFIGS,
  BLENDING_MODE 
} from '../../constants';

export default function AmbientParticles({ state }) {
  const particlesRef = useRef();
  const particleCount = PARTICLE_CONFIG.ambientParticleCount;
  
  const transitionRef = useRef({ speed: 0.12, spread: 0.15 });
  
  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const radius = 3.0 + Math.random() * 1.5;
      
      pos[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = radius * Math.cos(phi);
    }
    
    return pos;
  }, [particleCount]);
  
  useFrame((frameState, delta) => {
    if (!particlesRef.current) return;
    
    const target = AMBIENT_STATE_CONFIGS[state] || AMBIENT_STATE_CONFIGS.idle;
    const transition = transitionRef.current;
    const time = frameState.clock.elapsedTime;
    
    transition.speed += (target.speed - transition.speed) * 0.03;
    transition.spread += (target.spread - transition.spread) * 0.03;
    
    const pos = particlesRef.current.geometry.attributes.position.array;
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      let x = pos[i3];
      let y = pos[i3 + 1];
      let z = pos[i3 + 2];
      
      const angle = Math.atan2(z, x) + delta * transition.speed * (0.5 + Math.sin(i) * 0.3);
      const distance = Math.sqrt(x * x + z * z);
      const targetDist = 3.2 + Math.sin(time * 0.4 + i * 0.08) * transition.spread;
      const newDist = distance + (targetDist - distance) * 0.015;
      
      pos[i3] = Math.cos(angle) * newDist;
      pos[i3 + 2] = Math.sin(angle) * newDist;
      pos[i3 + 1] += Math.sin(time * 0.6 + i) * delta * transition.spread * 0.25;
      
      if (Math.abs(pos[i3 + 1]) > 3) pos[i3 + 1] *= -0.95;
    }
    
    particlesRef.current.geometry.attributes.position.needsUpdate = true;
  });
  
  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.012}
        color={PARTICLE_COLORS.ambientColor}
        transparent
        opacity={0.35}
        sizeAttenuation
        blending={BLENDING_MODE}
        depthWrite={false}
      />
    </points>
  );
}
