"use client";

import { RedirectPopupProvider } from '@/context/RedirectPopupContext';
import RedirectPopup from '@/components/RedirectPopup';

export default function Providers({ children }) {
  return (
    <RedirectPopupProvider>
      {children}
      <RedirectPopup />
    </RedirectPopupProvider>
  );
}
