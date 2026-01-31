"use client";

import ParticleOrb from './ParticleOrb';
import AmbientParticles from './AmbientParticles';
import GlowCore from './GlowCore';

export default function Scene({ state, audioIntensity }) {
  return (
    <>
      <ambientLight intensity={0.25} />
      <pointLight position={[5, 5, 5]} intensity={0.4} color="#2563eb" />
      <pointLight position={[-5, -5, -5]} intensity={0.3} color="#0891b2" />
      
      <GlowCore state={state} />
      <ParticleOrb state={state} audioIntensity={audioIntensity} />
      <AmbientParticles state={state} />
    </>
  );
}
