"use client";

import React, { createContext, useContext, useState, useCallback } from 'react';

const RedirectPopupContext = createContext(null);

export function RedirectPopupProvider({ children }) {
  const [popupType, setPopupType] = useState(null); // 'maps' | 'invoices' | null

  const showPopup = useCallback((type) => {
    setPopupType(type);
  }, []);

  const hidePopup = useCallback(() => {
    setPopupType(null);
  }, []);

  return (
    <RedirectPopupContext.Provider value={{ popupType, showPopup, hidePopup }}>
      {children}
    </RedirectPopupContext.Provider>
  );
}

export function useRedirectPopup() {
  const context = useContext(RedirectPopupContext);
  if (!context) {
    throw new Error('useRedirectPopup must be used within a RedirectPopupProvider');
  }
  return context;
}
