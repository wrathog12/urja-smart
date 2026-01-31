"use client";

import { useRef, useCallback } from 'react';
import { AUDIO_CONFIG } from '../constants';

export default function useAudio({ onSilence, onAudioChunk, setAudioIntensity }) {
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const streamRef = useRef(null);
  const rafIdRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const lastVoiceActivityTimeRef = useRef(Date.now());
  
  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };
  
  const setupMediaRecorder = useCallback((stream) => {
    try {
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          if (onAudioChunk) {
            try {
              const base64Data = await blobToBase64(event.data);
              onAudioChunk(base64Data);
            } catch (err) {
              console.error('Error converting audio:', err);
            }
          }
        }
      };
      
      mediaRecorder.start(AUDIO_CONFIG.recordingInterval);
    } catch (err) {
      console.error('Error setting up MediaRecorder:', err);
    }
  }, [onAudioChunk]);
  
  const updateAudioIntensity = useCallback(() => {
    if (!analyserRef.current) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    // Focus on voice frequency range (roughly 80Hz - 3000Hz)
    const voiceRangeEnd = Math.min(20, bufferLength);
    let sum = 0;
    let maxVal = 0;
    for (let i = 1; i < voiceRangeEnd; i++) {
      sum += dataArray[i];
      maxVal = Math.max(maxVal, dataArray[i]);
    }
    const average = sum / voiceRangeEnd;
    
    // Amplify the normalized value for more visible effect
    const normalizedAvg = average / 255;
    const normalizedPeak = maxVal / 255;
    const combined = (normalizedAvg * 0.6 + normalizedPeak * 0.4);
    
    // Amplify and clamp
    const amplified = Math.min(combined * 2.5, 1.0);
    
    setAudioIntensity(amplified);
    
    if (average > AUDIO_CONFIG.silenceThreshold) {
      lastVoiceActivityTimeRef.current = Date.now();
    } else if (Date.now() - lastVoiceActivityTimeRef.current > AUDIO_CONFIG.silenceTimeout && onSilence) {
      onSilence();
    }
    
    rafIdRef.current = requestAnimationFrame(updateAudioIntensity);
  }, [onSilence, setAudioIntensity]);
  
  const setupAudio = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = AUDIO_CONFIG.fftSize;
      analyser.smoothingTimeConstant = AUDIO_CONFIG.smoothingTimeConstant;
      analyserRef.current = analyser;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      sourceRef.current = source;
      
      setupMediaRecorder(stream);
      lastVoiceActivityTimeRef.current = Date.now();
      updateAudioIntensity();
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  }, [setupMediaRecorder, updateAudioIntensity]);
  
  const cleanupAudio = useCallback(() => {
    if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
    if (mediaRecorderRef.current?.state !== 'inactive') mediaRecorderRef.current?.stop();
    streamRef.current?.getTracks().forEach(track => track.stop());
    audioContextRef.current?.close();
    
    setAudioIntensity(0);
    rafIdRef.current = null;
    streamRef.current = null;
    audioContextRef.current = null;
    analyserRef.current = null;
    sourceRef.current = null;
    mediaRecorderRef.current = null;
  }, [setAudioIntensity]);
  
  return {
    setupAudio,
    cleanupAudio,
  };
}
