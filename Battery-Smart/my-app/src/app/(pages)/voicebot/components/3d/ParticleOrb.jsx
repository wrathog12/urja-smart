"use client";

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { 
  PARTICLE_CONFIG, 
  PARTICLE_COLORS, 
  ORB_STATE_CONFIGS,
  BLENDING_MODE 
} from '../../constants';

// Noise function for organic movement
const noise3D = (x, y, z, time) => {
  const n1 = Math.sin(x * 2.5 + time) * Math.cos(y * 2.5 + time * 0.7);
  const n2 = Math.sin(y * 3.0 + time * 1.1) * Math.cos(z * 2.0 + time * 0.8);
  const n3 = Math.sin(z * 2.8 + time * 0.9) * Math.cos(x * 2.2 + time * 1.2);
  return (n1 + n2 + n3) / 3;
};

export default function ParticleOrb({ state, audioIntensity = 0 }) {
  const pointsRef = useRef();
  const audioIntensityRef = useRef(0);
  const smoothedAudioBoostRef = useRef(0);
  
  const { orbParticleCount: particleCount, orbRadius } = PARTICLE_CONFIG;
  
  // Update ref on every render to get latest value in animation loop
  audioIntensityRef.current = audioIntensity;
  
  // Transition ref for smooth animations
  const transitionRef = useRef({
    noiseSpeed: 0.3,
    noiseStrength: 0.06,
    pulseSpeed: 0.5,
    pulseStrength: 0.02,
    rotationSpeed: 0.08,
    particleSize: 0.028,
    spread: 0.04
  });
  
  // Generate initial particle positions on sphere surface
  const [basePositions, colors, sizes] = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const cols = new Float32Array(particleCount * 3);
    const szs = new Float32Array(particleCount);
    
    const color1 = new THREE.Color(PARTICLE_COLORS.color1);
    const color2 = new THREE.Color(PARTICLE_COLORS.color2);
    const color3 = new THREE.Color(PARTICLE_COLORS.color3);
    const color4 = new THREE.Color(PARTICLE_COLORS.color4);
    
    for (let i = 0; i < particleCount; i++) {
      // Fibonacci spiral distribution for even coverage
      const phi = Math.acos(1 - 2 * (i + 0.5) / particleCount);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      
      positions[i * 3] = orbRadius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = orbRadius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = orbRadius * Math.cos(phi);
      
      // Varied colors
      const colorMix = Math.random();
      let particleColor;
      if (colorMix < 0.25) {
        particleColor = color1.clone().lerp(color2, Math.random());
      } else if (colorMix < 0.5) {
        particleColor = color2.clone().lerp(color3, Math.random());
      } else if (colorMix < 0.75) {
        particleColor = color3.clone().lerp(color4, Math.random());
      } else {
        particleColor = color4.clone().lerp(color1, Math.random());
      }
      
      cols[i * 3] = particleColor.r;
      cols[i * 3 + 1] = particleColor.g;
      cols[i * 3 + 2] = particleColor.b;
      
      szs[i] = 0.02 + Math.random() * 0.015;
    }
    
    return [positions, cols, szs];
  }, [particleCount, orbRadius]);
  
  const originalPositions = useMemo(() => new Float32Array(basePositions), [basePositions]);
  
  // Animation loop
  useFrame((frameState, delta) => {
    if (!pointsRef.current) return;
    
    const time = frameState.clock.elapsedTime;
    const target = ORB_STATE_CONFIGS[state] || ORB_STATE_CONFIGS.idle;
    const transition = transitionRef.current;
    
    // Smooth transitions
    const lerpSpeed = 0.04;
    Object.keys(target).forEach(key => {
      transition[key] += (target[key] - transition[key]) * lerpSpeed;
    });
    
    // Audio intensity affects particles - only for listening and speaking
    const isVoiceActive = state === 'listening' || state === 'speaking';
    const currentIntensity = audioIntensityRef.current;
    const targetAudioBoost = isVoiceActive ? currentIntensity * 0.6 : 0;
    
    // Smooth audio boost transition
    const lerpRate = targetAudioBoost > smoothedAudioBoostRef.current ? 0.15 : 0.03;
    smoothedAudioBoostRef.current += (targetAudioBoost - smoothedAudioBoostRef.current) * lerpRate;
    const audioBoost = smoothedAudioBoostRef.current;
    
    const positions = pointsRef.current.geometry.attributes.position.array;
    const sizesAttr = pointsRef.current.geometry.attributes.size.array;
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3;
      
      const ox = originalPositions[i3];
      const oy = originalPositions[i3 + 1];
      const oz = originalPositions[i3 + 2];
      
      const radius = Math.sqrt(ox * ox + oy * oy + oz * oz);
      const nx = ox / radius;
      const ny = oy / radius;
      const nz = oz / radius;
      
      // Noise-based displacement
      const noiseTime = time * transition.noiseSpeed;
      const noiseValue = noise3D(ox * 0.8, oy * 0.8, oz * 0.8, noiseTime);
      
      // Pulsing
      const pulse = Math.sin(time * transition.pulseSpeed + i * 0.008) * transition.pulseStrength;
      
      // Flutter for organic movement
      const flutter = Math.sin(time * 4 + i * 0.5) * transition.spread * 0.2;
      
      // Audio reactivity
      const wavePhase = Math.sin(i * 0.2 + time * 10) * 0.5 + 0.5;
      const audioDisplacement = audioBoost * (0.5 + wavePhase * 0.4);
      
      // Combined displacement
      const baseDisplacement = noiseValue * transition.noiseStrength + pulse + flutter;
      const displacement = baseDisplacement + audioDisplacement;
      
      const newRadius = radius + displacement;
      
      positions[i3] = nx * newRadius;
      positions[i3 + 1] = ny * newRadius;
      positions[i3 + 2] = nz * newRadius;
      
      // Size responds to audio
      const sizeMultiplier = 1 + audioBoost * 0.8;
      sizesAttr[i] = sizes[i] * sizeMultiplier * (transition.particleSize / 0.028);
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
    pointsRef.current.geometry.attributes.size.needsUpdate = true;
    
    // Rotation
    pointsRef.current.rotation.y += delta * transition.rotationSpeed;
    pointsRef.current.rotation.x = Math.sin(time * 0.15) * 0.08;
    pointsRef.current.rotation.z = Math.cos(time * 0.1) * 0.04;
    
    // Opacity
    pointsRef.current.material.opacity = state === 'idle' || state === 'thinking' ? 0.75 : 0.9;
  });
  
  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={basePositions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          count={particleCount}
          array={sizes}
          itemSize={1}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.03}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={BLENDING_MODE}
        depthWrite={false}
      />
    </points>
  );
}
