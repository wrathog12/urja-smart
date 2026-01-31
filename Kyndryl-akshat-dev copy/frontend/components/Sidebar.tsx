"use client";
import { FiMenu } from "react-icons/fi";
import { RiChatNewLine } from "react-icons/ri";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChatSummary } from "@/types/chat";
import ProfileButton from "./ProfileIcon";
import { User } from "@/types/user";

const Sidebar = () => {
  const router = useRouter();
  const [expanded, setExpanded] = useState(false);
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [loading, setLoading] = useState(false);

  const handleNewChat = () => {
    router.push("/");
  };

  const handleMenuClick = () => {
    setExpanded((prev) => !prev);
  };

  useEffect(() => {
    if (expanded) {
      setLoading(true);
      fetch("/api/chats")
        .then((res) => res.json())
        .then((data) => setChats(data.chats))
        .finally(() => setLoading(false));
    }
  }, [expanded]);

  const openChat = (id: string) => {
    router.push(`/chat/${id}/`);
  };

  const guestUser: User = {
    id: "guest",
    name: "Guest",
    email: "guest@example.com",
    conversations: [],
  };

  return (
    <motion.aside
  initial={{ width: "4rem" }}
  animate={{ width: expanded ? "16rem" : "4rem" }}
  transition={{ duration: 0.3, ease: "easeInOut" }}
  className="fixed top-0 left-0 z-10 h-screen bg-[#0D1218] flex flex-col justify-between border-r border-neutral-800 hidden md:flex"
>
  {/* Top: Menu + New Chat + Chats */}
  <div className="flex flex-col flex-1">
    {/* Menu + New Chat */}
    <div className="flex flex-col items-start gap-2 px-2 pt-5">
      {/* Menu button */}
      <button
        className="flex items-center text-neutral-400 hover:text-white transition-colors cursor-pointer ml-4 py-2 w-full"
        onClick={handleMenuClick}
        title="Menu"
      >
        <FiMenu size={20} />
        <motion.span
          initial={false}
          animate={{
            opacity: expanded ? 1 : 0,
            width: expanded ? "auto" : 0,
            marginLeft: expanded ? 12 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="text-base font-medium text-neutral-200 overflow-hidden whitespace-nowrap"
        >
          Menu
        </motion.span>
      </button>

      {/* New Chat button */}
      <button
        className="flex items-center text-neutral-400 hover:text-white transition-colors cursor-pointer ml-4 py-2 w-full"
        onClick={handleNewChat}
        title="New Chat"
      >
        <RiChatNewLine size={20} />
        <motion.span
          initial={false}
          animate={{
            opacity: expanded ? 1 : 0,
            width: expanded ? "auto" : 0,
            marginLeft: expanded ? 12 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="text-base font-medium text-neutral-200 overflow-hidden whitespace-nowrap"
        >
          New Chat
        </motion.span>
      </button>
    </div>

    {/* Chat list */}
    <div className="mt-10 flex-1 overflow-y-auto px-4">
      <motion.h2
        initial={false}
        animate={{ opacity: expanded ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        className="text-neutral-300 mb-3 text-sm font-semibold overflow-hidden whitespace-nowrap"
      >
        Chats
      </motion.h2>
      {loading ? (
        <div className="text-neutral-500 text-xs">Loading...</div>
      ) : (
        <ul>
          {chats.map((chat) => (
            <li
              key={chat.id}
              onClick={() => openChat(chat.id)}
              className="flex items-center px-2 py-1 rounded cursor-pointer hover:bg-neutral-800 text-sm text-neutral-200"
              title={chat.title}
            >
              <div className="w-2 h-2 bg-neutral-500 rounded-full shrink-0" />
              <motion.span
                initial={false}
                animate={{
                  opacity: expanded ? 1 : 0,
                  width: expanded ? "auto" : 0,
                }}
                transition={{ duration: 0.2 }}
                className="ml-3 truncate overflow-hidden whitespace-nowrap"
              >
                {chat.title}
              </motion.span>
            </li>
          ))}
        </ul>
      )}
    </div>
  </div>
  {/* Bottom: Profile */}
  <div className="flex items-center ml-4">
      <ProfileButton expanded={expanded} user={guestUser} />
  </div>
  


</motion.aside>

  );
};

export default Sidebar;