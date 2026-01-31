import * as THREE from 'three';

// Particle configuration
export const PARTICLE_CONFIG = {
  orbParticleCount: 2500,
  orbRadius: 2.2,
  ambientParticleCount: 120,
};

// Colors for particles
export const PARTICLE_COLORS = {
  color1: '#2563eb', // blue-600
  color2: '#3b82f6', // blue-500
  color3: '#0891b2', // cyan-600
  color4: '#14b8a6', // teal-500
  ambientColor: '#3b82f6',
  glowColor: '#2563eb',
};

// State configurations for particle orb animation
export const ORB_STATE_CONFIGS = {
  idle: {
    noiseSpeed: 0.3,
    noiseStrength: 0.06,
    pulseSpeed: 0.5,
    pulseStrength: 0.02,
    rotationSpeed: 0.08,
    particleSize: 0.028,
    spread: 0.04
  },
  thinking: {
    noiseSpeed: 0.3,
    noiseStrength: 0.06,
    pulseSpeed: 0.5,
    pulseStrength: 0.02,
    rotationSpeed: 0.08,
    particleSize: 0.028,
    spread: 0.04
  },
  listening: {
    noiseSpeed: 0.6,
    noiseStrength: 0.12,
    pulseSpeed: 1.2,
    pulseStrength: 0.06,
    rotationSpeed: 0.15,
    particleSize: 0.032,
    spread: 0.1
  },
  speaking: {
    noiseSpeed: 0.6,
    noiseStrength: 0.12,
    pulseSpeed: 1.2,
    pulseStrength: 0.06,
    rotationSpeed: 0.15,
    particleSize: 0.032,
    spread: 0.1
  }
};

// State configurations for ambient particles
export const AMBIENT_STATE_CONFIGS = {
  idle: { speed: 0.12, spread: 0.15 },
  thinking: { speed: 0.12, spread: 0.15 },
  listening: { speed: 0.25, spread: 0.35 },
  speaking: { speed: 0.25, spread: 0.35 }
};

// State intensities for glow core
export const GLOW_STATE_INTENSITIES = {
  idle: 0.12,
  thinking: 0.12,
  listening: 0.25,
  speaking: 0.25
};

// Audio configuration
export const AUDIO_CONFIG = {
  fftSize: 256,
  smoothingTimeConstant: 0.5,
  silenceThreshold: 8,
  silenceTimeout: 5000, // 5 seconds
  recordingInterval: 1000, // 1 second chunks
};

// Camera configuration
export const CAMERA_CONFIG = {
  position: [0, 0, 6],
  fov: 50,
};

// Status text mapping
export const STATUS_TEXT = {
  idle: 'Standby Mode',
  listening: 'Listening...',
  thinking: 'Processing...',
  speaking: 'Speaking...',
};

// THREE.js blending mode export for components
export const BLENDING_MODE = THREE.AdditiveBlending;
