"use client";

import React, { useRef, useState, forwardRef, useImperativeHandle, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Scene } from './3d';
import { useAudio } from '../hooks';
import { STATUS_TEXT, CAMERA_CONFIG } from '../constants';

const VoiceAgent = forwardRef(function VoiceAgent({ 
  state = 'idle', 
  onSilence, 
  onAudioChunk, 
  speakingIntensity = 0 
}, ref) {
  const [audioIntensity, setAudioIntensity] = useState(0);
  const containerRef = useRef(null);
  
  // Audio hook
  const { setupAudio, cleanupAudio } = useAudio({
    onSilence,
    onAudioChunk,
    setAudioIntensity,
  });
  
  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    setAudioIntensity: (intensity) => setAudioIntensity(intensity)
  }));
  
  // Use speaking intensity when speaking
  const effectiveIntensity = state === 'speaking' ? speakingIntensity : audioIntensity;
  
  // Setup/cleanup audio based on state
  useEffect(() => {
    if (state === 'listening') {
      setupAudio();
    } else {
      cleanupAudio();
    }
    return () => cleanupAudio();
  }, [state, setupAudio, cleanupAudio]);
  
  const getStatusText = () => STATUS_TEXT[state] || STATUS_TEXT.idle;
  
  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-2">
      <div 
        ref={containerRef}
        className="relative w-80 h-80 md:w-96 md:h-96 lg:w-[420px] lg:h-[420px]"
      >
        <Canvas
          camera={{ position: CAMERA_CONFIG.position, fov: CAMERA_CONFIG.fov }}
          gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
          style={{ background: 'transparent' }}
        >
          <Scene state={state} audioIntensity={effectiveIntensity} />
        </Canvas>
        
        <div 
          className={`absolute inset-0 rounded-full pointer-events-none transition-opacity duration-1000 ${
            state === 'idle' || state === 'thinking' ? 'opacity-5' : 'opacity-15'
          }`}
          style={{
            background: 'radial-gradient(circle at center, rgba(37, 99, 235, 0.2) 0%, transparent 55%)',
            filter: 'blur(30px)'
          }}
        />
      </div>
      
      <div className="text-center">
        <p className={`text-sm font-medium uppercase tracking-[0.3em] transition-all duration-500 ${
          state === 'idle' || state === 'thinking' ? 'text-gray-400' : 'text-blue-500'
        }`}>
          {getStatusText()}
        </p>
      </div>
    </div>
  );
});

export default VoiceAgent;
