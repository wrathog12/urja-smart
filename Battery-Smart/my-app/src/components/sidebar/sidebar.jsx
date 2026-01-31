"use client";

import React, { useEffect, useRef, useState } from 'react';
import { 
  Map,
  ShieldUser,
  Bot,
  LayoutDashboard,
  AudioLines,
  Menu,
  X,
  Battery,
  ReceiptIndianRupee,
  MenuIcon,
  Settings,
  UserPlus,
  Gauge
} from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import logo from '../../assets/logo.png';

const defaultNavItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/maps', label: 'Maps', icon: Map },
  // { href: 'http://localhost:3001/', label: 'Chatbot', icon: Bot},
  // { href: '/admin', label: 'Admin', icon: ShieldUser },
];

const partnerNavItems = [
  { href: '/onboard', label: 'Onboard', icon: UserPlus },
  { href: '/partnerDashboard', label: 'Partner Dashboard', icon: Gauge },
];

const dropdownItems = [
  { href: '/invoices', label: 'Invoices', icon: ReceiptIndianRupee},
  { href: '/partner', label: 'Partner', icon: ShieldUser},
  { href: '/settings', label: 'Settings', icon: Settings},
];

export default function Navbar({ children }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const isActive = (href) => pathname === href;
  
  // Determine which nav items to show based on current route
  const isPartnerRoute = pathname.startsWith('/partner') || pathname.startsWith('/partnerDashboard') || pathname.startsWith('/onboard');
  const navItems = isPartnerRoute ? partnerNavItems : defaultNavItems;

    const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center">
            <Image src={logo} alt="Battery Smart Logo" width={52} height={52} />
            <span className="font-semibold text-xl text-blue-600 hidden sm:block">
              Battery Smart
            </span>
          </Link>

          

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <button
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-50 text-green-600'
                      : 'text-blue-400 hover:bg-blue-50 hover:text-green-600'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="text-sm">{item.label}</span>
                </button>
              </Link>
            ))}
            
            {/* Dropdown Container - Hidden on partner routes */}
            {!isPartnerRoute && (
            <div ref={ref} className="relative">
              <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors text-blue-400 hover:bg-blue-50 hover:text-green-600"
              >
                <MenuIcon className="w-4 h-4" />
                <span className="text-sm">Menu</span>
              </button>

              {/* Dropdown */}
              {open && (
                <div className="absolute top-full -right-8 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-[160px] z-50">
                  {dropdownItems.map((item) => (
                    <Link key={item.href} href={item.href}>
                      <button
                        onClick={() => setOpen(false)}
                        className={`w-full flex items-center gap-2 px-10 py-2 font-medium  transition-colors ${
                          isActive(item.href)
                            ? 'bg-blue-50 text-green-600'
                            : 'text-blue-400 hover:bg-blue-50 hover:text-green-600'
                        }`}
                      >
                        <item.icon className="w-4 h-4" />
                        <span className="text-sm">{item.label}</span>
                      </button>
                    </Link>
                  ))}
                </div>
              )}
            </div>
            )}
            
          </div>

          <div className="flex items-center gap-2 mr-6">
            <Link href="/">
              {/* Battery Button with Charging Animation */}
              <div className="group hidden md:flex relative cursor-pointer">
                {/* Battery Body */}
                <div className={`relative flex items-center justify-center px-5 py-2 border-2 rounded-lg overflow-hidden transition-all duration-300 ${
                  isActive('/')
                    ? 'border-green-500 bg-green-50'
                    : 'border-blue-600 bg-white hover:border-blue-600'
                }`}>
                  {/* Charging Fill Animation */}
                  <div className={`absolute left-0 top-0 h-full bg-green-400 transition-all duration-700 ease-out ${
                    isActive('/') 
                      ? 'w-full' 
                      : 'w-0 group-hover:w-full'
                  }`} />
                  
                  {/* Content */}
                  <div className={`relative z-10 flex items-center gap-2 font-medium transition-colors duration-300 ${
                    isActive('/')
                      ? 'text-blue-700'
                      : 'text-blue-600 group-hover:text-blue-600'
                  }`}>
                    <AudioLines className="w-4 h-4" />
                    <span className="text-sm">Urja Bot</span>
                  </div>
                </div>
                
                {/* Battery Head */}
                <div className={`absolute -right-2 top-1/2 -translate-y-1/2 w-2 h-4 rounded-r-sm transition-colors duration-300 ${
                  isActive('/voicebot')
                    ? 'bg-green-500'
                    : 'bg-blue-600 group-hover:bg-green-500'
                }`} />
              </div>
            </Link>
            
            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5 text-gray-600" />
              ) : (
                <Menu className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
          
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-3 border-t border-gray-100">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href}>
                  <button
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-green-50 text-green-600'
                        : 'text-gray-600 hover:bg-green-50 hover:text-green-600'
                    }`}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </button>
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-gray-50">
        {children}
      </div>
    </div>
  );
}