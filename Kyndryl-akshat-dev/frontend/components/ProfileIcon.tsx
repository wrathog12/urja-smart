"use client";

import { useRef, useState, useEffect } from "react";
import { FaUser } from "react-icons/fa";
import { User } from "@/types/user";

type ProfileButtonProps = {
  user: User;
  expanded?: boolean;
};

const ProfileButton = ({
  user,
  expanded = false,
}: ProfileButtonProps) => {
  const name = user?.name || "User";
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Close dropdown on outside click
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (!containerRef.current?.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={containerRef} className="relative flex items-center pb-2 w-full">
      <button
        className="flex items-center justify-center h-8 w-8 rounded-full bg-blue-500 text-white cursor-pointer hover:bg-blue-600 transition-colors shrink-0"
        title="Profile"
        onClick={() => setOpen((v) => !v)}
      >
        <FaUser size={16} />
      </button>

      {expanded && (
        <span
          className="text-base font-medium text-white overflow-hidden whitespace-nowrap cursor-pointer ml-3"
          onClick={() => setOpen((v) => !v)}
        >
          {name}
        </span>
      )}

      {open && (
        <div 
          className="fixed left-3 bottom-12 min-w-[260px] bg-[#15181e] border border-[#2a2d34] rounded-xl shadow-lg p-2 z-[9999]"
          style={{
            transform: expanded ? 'translateX(0)' : 'translateX(0)',
          }}
        >
          <div className="flex items-center gap-2 p-2">
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-500 text-white shrink-0">
              <FaUser size={14} />
            </div>
            <div className="flex-1">
              <div className="font-medium text-white text-sm leading-tight">{name}</div>
              <div className="text-xs text-[#a0a6b8]">Free</div>
            </div>
          </div>
          <div className="border-t border-[#23242b] my-1" />
          <div className="flex flex-col gap-0">
            <div className="text-xs text-[#e3e6ef] hover:bg-[#1c1f27] px-3 py-2 cursor-pointer rounded transition-colors">
              Upgrade Plan
            </div>
            <div className="text-xs text-[#e3e6ef] hover:bg-[#1c1f27] px-3 py-2 cursor-pointer rounded transition-colors">
              Settings
            </div>
          </div>
          <div className="border-t border-[#23242b] my-1" />
          <div className="text-xs text-red-500 cursor-pointer hover:bg-[#1c1f27] px-3 py-2 rounded transition-colors">
            Log out
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileButton;