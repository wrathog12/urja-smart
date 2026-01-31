"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useRedirectPopup } from '@/context/RedirectPopupContext';
import { Map, FileText, X, ChevronRight, MapPin, Receipt } from 'lucide-react';

export default function RedirectPopup() {
  const { popupType, hidePopup } = useRedirectPopup();
  const router = useRouter();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    console.log('RedirectPopup: popupType changed to:', popupType);
    if (popupType) {
      // Small delay for animation
      setTimeout(() => setIsVisible(true), 50);
    } else {
      setIsVisible(false);
    }
  }, [popupType]);

  const handleNavigate = () => {
    const path = popupType === 'maps' ? '/maps' : '/invoices';
    hidePopup();
    router.push(path);
  };

  const handleClose = (e) => {
    e.stopPropagation();
    setIsVisible(false);
    setTimeout(hidePopup, 300);
  };

  if (!popupType) return null;

  return (
    <div 
      className={`
        fixed bottom-6 left-1/2 -translate-x-1/2 z-[9999]
        transition-all duration-300 ease-out
        ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}
      `}
    >
      <div 
        onClick={handleNavigate}
        className="
          relative cursor-pointer
          px-5 py-4 rounded-2xl shadow-2xl
          flex items-center gap-4 min-w-[320px] max-w-[420px]
          hover:scale-[1.02] transition-transform duration-200
        "
        style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.8)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(34, 197, 94, 0.1)',
        }}
      >
        {/* Close button */}
        <button
          onClick={handleClose}
          className="absolute -top-2 -right-2 p-1.5 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors shadow-md"
        >
          <X className="w-3.5 h-3.5 text-gray-600" />
        </button>

        {/* Icon */}
        <div 
          className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center"
          style={{
            background: popupType === 'maps' 
              ? 'linear-gradient(135deg, #22c55e 0%, #10b981 100%)'
              : 'linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)',
            boxShadow: popupType === 'maps'
              ? '0 4px 14px rgba(34, 197, 94, 0.4)'
              : '0 4px 14px rgba(59, 130, 246, 0.4)',
          }}
        >
          {popupType === 'maps' ? (
            <MapPin className="w-7 h-7 text-white" />
          ) : (
            <Receipt className="w-7 h-7 text-white" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1">
          <h4 className="font-bold text-gray-800 text-sm mb-0.5">
            {popupType === 'maps' ? 'Nearby Swap Stations' : 'Your Invoice'}
          </h4>
          <p className="text-xs text-gray-500">
            {popupType === 'maps' 
              ? 'View map with nearest stations' 
              : 'View your billing details'}
          </p>
        </div>

        {/* Arrow */}
        <div 
          className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
          style={{
            background: popupType === 'maps' 
              ? 'rgba(34, 197, 94, 0.1)' 
              : 'rgba(59, 130, 246, 0.1)',
          }}
        >
          <ChevronRight 
            className={`w-5 h-5 ${popupType === 'maps' ? 'text-emerald-600' : 'text-blue-600'}`} 
          />
        </div>

        {/* Animated border glow */}
        <div 
          className="absolute inset-0 rounded-2xl pointer-events-none"
          style={{
            background: popupType === 'maps'
              ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, transparent 50%)'
              : 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
          }}
        />
      </div>
    </div>
  );
}
