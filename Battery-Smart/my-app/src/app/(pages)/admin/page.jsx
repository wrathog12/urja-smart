"use client";

import React, { useState, useEffect } from "react";
import { adminSocket } from "./services/adminSocket";
import {
  Monitor,
  MessageSquare,
  Mic,
  Clock,
  Hash,
  AlertTriangle,
  CheckCircle,
  User,
  Bot,
  BarChart3,
  FileText,
  TrendingDown,
  TrendingUp,
  Activity,
  Phone,
  PhoneCall,
} from "lucide-react";

// Confidence badge component
const ConfidenceBadge = ({ confidence }) => {
  if (confidence === null || confidence === undefined) return null;

  const percentage = Math.round(confidence * 100);
  const colorClass =
    percentage >= 80
      ? "bg-green-100 text-green-700"
      : percentage >= 60
        ? "bg-yellow-100 text-yellow-700"
        : "bg-red-100 text-red-700";

  return (
    <span
      className={`ml-2 px-1.5 py-0.5 rounded text-xs font-mono ${colorClass}`}
    >
      {percentage}%
    </span>
  );
};

export default function AdminPage() {
  const [sessions, setSessions] = useState([]);
  const [escalations, setEscalations] = useState([]);
  const [selectedEscalation, setSelectedEscalation] = useState(null);

  useEffect(() => {
    adminSocket.connect((data) => {
      if (data.type === "SYNC") {
        setSessions(data.sessions || []);
        setEscalations(data.escalations || []);
      } else if (data.type === "SESSION_STARTED") {
        setSessions((prev) => [...prev, data.session]);
      } else if (data.type === "SESSION_ENDED") {
        setSessions((prev) => prev.filter((s) => s.id !== data.id));
      }
    });

    // Set escalation-specific callbacks
    adminSocket.setEscalationCallbacks({
      onNew: (escalation) => {
        setEscalations((prev) => [...prev, escalation]);
      },
      onResolved: (escalationId) => {
        setEscalations((prev) => prev.filter((e) => e.id !== escalationId));
        setSelectedEscalation((prev) =>
          prev?.id === escalationId ? null : prev,
        );
      },
      onUpdated: (escalation) => {
        setEscalations((prev) =>
          prev.map((e) => (e.id === escalation.id ? escalation : e)),
        );
      },
    });

    return () => adminSocket.disconnect();
  }, []);

  const handleResolve = (escalationId) => {
    adminSocket.resolveEscalation(escalationId);
  };

  return (
    <div className="p-8 max-w-8xl space-y-8 bg-white min-h-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-gray-800">
            System Monitor
          </h1>
        </div>
        <div className="flex items-center gap-4">
          {escalations.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-xl border border-red-200">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-red-600">
                {escalations.length} Escalations
              </span>
            </div>
          )}
          <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-xl border border-gray-200">
            <span className="font-medium text-gray-600">
              {sessions.length} Active Sessions
            </span>
          </div>
        </div>
      </div>

      {/* Escalations Section */}
      {escalations.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-red-600 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Escalated Calls - Needs Attention
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {escalations.map((escalation) => (
              <div
                key={escalation.id}
                className={`bg-white rounded-lg border-2 ${
                  selectedEscalation?.id === escalation.id
                    ? "border-red-400"
                    : "border-red-200"
                } p-4 hover:border-red-400 transition-all cursor-pointer`}
                onClick={() =>
                  setSelectedEscalation(
                    selectedEscalation?.id === escalation.id
                      ? null
                      : escalation,
                  )
                }
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div
                      className={`p-2 rounded-lg ${escalation.type === "voice" ? "bg-sky-50 text-sky-500" : "bg-emerald-50 text-emerald-500"}`}
                    >
                      {escalation.type === "voice" ? (
                        <Mic size={20} />
                      ) : (
                        <MessageSquare size={20} />
                      )}
                    </div>
                    <div>
                      <span className="font-semibold text-gray-800 capitalize">
                        {escalation.type} Escalation
                      </span>
                      <p className="text-xs text-gray-500">
                        Session: {escalation.sessionId}
                      </p>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider ${
                      escalation.status === "pending"
                        ? "bg-red-100 text-red-600"
                        : "bg-yellow-100 text-yellow-600"
                    }`}
                  >
                    {escalation.status}
                  </span>
                </div>

                <div className="text-sm text-gray-600 mb-3">
                  <strong>Reason:</strong> {escalation.reason}
                </div>

                {/* Summary Section */}
                {escalation.summary && (
                  <div className="mb-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="flex items-center gap-2 text-blue-700 text-xs font-semibold mb-1">
                      <FileText size={14} />
                      SUMMARY
                    </div>
                    <p className="text-sm text-blue-800">
                      {escalation.summary}
                    </p>
                  </div>
                )}

                {/* Stats Row */}
                {escalation.stats && (
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div className="text-lg font-bold text-gray-700">
                        {escalation.stats.totalTurns || 0}
                      </div>
                      <div className="text-xs text-gray-500">Total Turns</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div
                        className={`text-lg font-bold ${
                          (escalation.stats.avgConfidence || 0) >= 0.7
                            ? "text-green-600"
                            : (escalation.stats.avgConfidence || 0) >= 0.5
                              ? "text-yellow-600"
                              : "text-red-600"
                        }`}
                      >
                        {escalation.stats.avgConfidence
                          ? Math.round(escalation.stats.avgConfidence * 100) +
                            "%"
                          : "N/A"}
                      </div>
                      <div className="text-xs text-gray-500">
                        Avg Confidence
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-2 text-center">
                      <div
                        className={`text-lg font-bold ${
                          (escalation.stats.lowConfidenceCount || 0) > 2
                            ? "text-red-600"
                            : "text-gray-700"
                        }`}
                      >
                        {escalation.stats.lowConfidenceCount || 0}
                      </div>
                      <div className="text-xs text-gray-500">
                        Low Conf. Msgs
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
                  <Clock size={14} />
                  <span>{new Date(escalation.createdAt).toLocaleString()}</span>
                  {/* Customer Phone Number */}
                  {escalation.customerPhone && (
                    <>
                      <span className="text-gray-300">|</span>
                      <Phone size={14} />
                      <span>{escalation.customerPhone}</span>
                    </>
                  )}
                </div>

                {/* Full Transcript with Confidence Scores */}
                {selectedEscalation?.id === escalation.id &&
                  escalation.history &&
                  escalation.history.length > 0 && (
                    <div className="mt-4 border-t pt-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                          <Activity size={16} />
                          Full Transcript ({escalation.history.length} messages)
                        </h4>
                        {escalation.type === "voice" && (
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <BarChart3 size={12} />
                            Confidence scores shown
                          </span>
                        )}
                      </div>
                      <div className="space-y-2 max-h-80 overflow-y-auto bg-gray-50 rounded-lg p-3">
                        {escalation.history.map((msg, idx) => (
                          <div
                            key={idx}
                            className={`flex gap-2 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={`flex items-start gap-2 max-w-[85%] ${msg.sender === "user" ? "flex-row-reverse" : ""}`}
                            >
                              <div
                                className={`w-6 h-6 rounded-full flex items-center justify-center text-white shrink-0 ${
                                  msg.sender === "user"
                                    ? "bg-gray-500"
                                    : "bg-sky-400"
                                }`}
                              >
                                {msg.sender === "user" ? (
                                  <User size={12} />
                                ) : (
                                  <Bot size={12} />
                                )}
                              </div>
                              <div className="flex flex-col">
                                <div
                                  className={`px-3 py-2 rounded-lg text-sm ${
                                    msg.sender === "user"
                                      ? "bg-sky-400 text-white"
                                      : "bg-white border border-gray-200 text-gray-700"
                                  }`}
                                >
                                  {msg.text}
                                </div>
                                {/* Show confidence score and timestamp for user messages */}
                                {msg.sender === "user" && (
                                  <div className="flex items-center gap-2 mt-1 justify-end">
                                    {msg.confidence !== null &&
                                      msg.confidence !== undefined && (
                                        <span
                                          className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                                            msg.confidence >= 0.8
                                              ? "bg-green-100 text-green-700"
                                              : msg.confidence >= 0.6
                                                ? "bg-yellow-100 text-yellow-700"
                                                : "bg-red-100 text-red-700"
                                          }`}
                                        >
                                          {msg.confidence >= 0.8 ? (
                                            <TrendingUp
                                              size={10}
                                              className="inline mr-1"
                                            />
                                          ) : msg.confidence < 0.6 ? (
                                            <TrendingDown
                                              size={10}
                                              className="inline mr-1"
                                            />
                                          ) : null}
                                          {Math.round(msg.confidence * 100)}%
                                        </span>
                                      )}
                                    {msg.timestamp && (
                                      <span className="text-xs text-gray-400">
                                        {new Date(
                                          msg.timestamp,
                                        ).toLocaleTimeString()}
                                      </span>
                                    )}
                                  </div>
                                )}
                                {/* Show tool info for bot messages */}
                                {msg.sender === "bot" && msg.tool && (
                                  <div className="mt-1">
                                    <span className="px-1.5 py-0.5 rounded text-xs bg-purple-100 text-purple-700">
                                      🔧 {msg.tool}
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Action Buttons */}
                <div className="mt-3 space-y-2">
                  {/* Phone Number Display */}
                  {escalation.customerPhone && (
                    <div className="flex items-center justify-between bg-gray-100 rounded-lg px-3 py-2">
                      <div className="flex items-center gap-2">
                        <Phone size={14} className="text-gray-500" />
                        <span className="font-mono text-sm">
                          {escalation.customerPhone}
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigator.clipboard.writeText(
                            escalation.customerPhone,
                          );
                          alert("Phone number copied!");
                        }}
                        className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded transition-colors"
                      >
                        Copy
                      </button>
                    </div>
                  )}

                  {/* Call Options Row */}
                  <div className="flex gap-2">
                    {/* WhatsApp Chat Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const phone =
                          escalation.customerPhone ||
                          prompt(
                            "Enter phone (with country code, e.g., 919876543210):",
                          );
                        if (phone) {
                          window.open(
                            `https://wa.me/${phone.replace(/[^0-9]/g, "")}`,
                            "_blank",
                          );
                        }
                      }}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      title="Opens WhatsApp chat - then click call icon"
                    >
                      <svg
                        className="w-4 h-4"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                      >
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                      </svg>
                      WhatsApp
                    </button>

                    {/* Phone Link / Dialer Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        const phone =
                          escalation.customerPhone ||
                          prompt("Enter phone number:");
                        if (phone) {
                          window.location.href = `tel:${phone}`;
                        }
                      }}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                      title="Uses Phone Link or default dialer"
                    >
                      <PhoneCall size={16} />
                      Dial
                    </button>
                  </div>

                  <p className="text-xs text-gray-400 text-center">
                    💡 Use Windows Phone Link for free calling via your phone
                  </p>

                  {/* Resolve Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleResolve(escalation.id);
                    }}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                  >
                    <CheckCircle size={16} />
                    Mark Resolved
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Sessions Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          Active Sessions
        </h2>
        {sessions.length === 0 ? (
          <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 p-20 text-center">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 border border-gray-200">
              <Monitor className="text-gray-400 w-10 h-10" />
            </div>
            <h3 className="text-xl font-semibold text-gray-700">
              No Active Sessions
            </h3>
            <p className="text-gray-400 mt-2">
              Waiting for users to establish connections...
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="bg-white rounded-lg border border-gray-200 p-4 hover:border-sky-400 transition-all"
              >
                <div className="flex items-center align-center justify-between">
                  <div
                    className={`p-2 rounded-lg ${session.type === "voice" ? "bg-sky-50 text-sky-500" : "bg-emerald-50 text-emerald-500"}`}
                  >
                    {session.type === "voice" ? (
                      <Mic size={20} />
                    ) : (
                      <MessageSquare size={20} />
                    )}
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block px-3 py-1 rounded-lg text-xs font-medium uppercase tracking-wider
                      ${session.type === "voice" ? "bg-sky-100 text-sky-600" : "bg-emerald-100 text-emerald-600"}
                    `}
                    >
                      {session.type} Agent
                    </span>
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <div className="flex items-center gap-3 text-gray-600">
                    <Hash size={18} className="text-gray-400" />
                    <span className="font-mono text-sm font-medium truncate">
                      {session.id}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-600">
                    <Clock size={18} className="text-gray-400" />
                    <span className="text-xs font-medium text-gray-400">
                      Connected:{" "}
                      {new Date(session.startTime).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
