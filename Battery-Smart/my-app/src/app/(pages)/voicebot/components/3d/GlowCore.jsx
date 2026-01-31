"use client";

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { PARTICLE_COLORS, GLOW_STATE_INTENSITIES, BLENDING_MODE } from '../../constants';

export default function GlowCore({ state }) {
  const meshRef = useRef();
  const intensityRef = useRef(0.12);
  
  useFrame((frameState) => {
    if (!meshRef.current) return;
    
    const target = GLOW_STATE_INTENSITIES[state] || 0.12;
    intensityRef.current += (target - intensityRef.current) * 0.03;
    
    const pulse = Math.sin(frameState.clock.elapsedTime * 1.5) * 0.03;
    meshRef.current.material.opacity = intensityRef.current + pulse;
    
    const scale = 1 + Math.sin(frameState.clock.elapsedTime * 1.2) * 0.03;
    meshRef.current.scale.setScalar(scale);
  });
  
  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1.2, 32, 32]} />
      <meshBasicMaterial
        color={PARTICLE_COLORS.glowColor}
        transparent
        opacity={0.12}
        blending={BLENDING_MODE}
        depthWrite={false}
      />
    </mesh>
  );
}
