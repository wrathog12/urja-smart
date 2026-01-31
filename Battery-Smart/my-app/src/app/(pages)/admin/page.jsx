"use client";

import React, { useState, useEffect } from 'react';
import { adminSocket } from './services/adminSocket';
import { Monitor, MessageSquare, Mic, Clock, Hash, AlertTriangle, CheckCircle, User, Bot } from 'lucide-react';

export default function AdminPage() {
  const [sessions, setSessions] = useState([]);
  const [escalations, setEscalations] = useState([]);
  const [selectedEscalation, setSelectedEscalation] = useState(null);

  useEffect(() => {
    adminSocket.connect((data) => {
      if (data.type === 'SYNC') {
        setSessions(data.sessions || []);
        setEscalations(data.escalations || []);
      } else if (data.type === 'SESSION_STARTED') {
        setSessions(prev => [...prev, data.session]);
      } else if (data.type === 'SESSION_ENDED') {
        setSessions(prev => prev.filter(s => s.id !== data.id));
      }
    });

    // Set escalation-specific callbacks
    adminSocket.setEscalationCallbacks({
      onNew: (escalation) => {
        setEscalations(prev => [...prev, escalation]);
      },
      onResolved: (escalationId) => {
        setEscalations(prev => prev.filter(e => e.id !== escalationId));
        if (selectedEscalation?.id === escalationId) {
          setSelectedEscalation(null);
        }
      },
      onUpdated: (escalation) => {
        setEscalations(prev => prev.map(e => e.id === escalation.id ? escalation : e));
      }
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
          <h1 className="text-3xl font-semibold text-gray-800">System Monitor</h1>
        </div>
        <div className="flex items-center gap-4">
          {escalations.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-xl border border-red-200">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-red-600">{escalations.length} Escalations</span>
            </div>
          )}
          <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-xl border border-gray-200">
            <span className="font-medium text-gray-600">{sessions.length} Active Sessions</span>
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
                    ? 'border-red-400' 
                    : 'border-red-200'
                } p-4 hover:border-red-400 transition-all cursor-pointer`}
                onClick={() => setSelectedEscalation(selectedEscalation?.id === escalation.id ? null : escalation)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${escalation.type === 'voice' ? 'bg-sky-50 text-sky-500' : 'bg-emerald-50 text-emerald-500'}`}>
                      {escalation.type === 'voice' ? <Mic size={20} /> : <MessageSquare size={20} />}
                    </div>
                    <div>
                      <span className="font-semibold text-gray-800 capitalize">{escalation.type} Escalation</span>
                      <p className="text-xs text-gray-500">Session: {escalation.sessionId}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wider ${
                    escalation.status === 'pending' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'
                  }`}>
                    {escalation.status}
                  </span>
                </div>

                <div className="text-sm text-gray-600 mb-3">
                  <strong>Reason:</strong> {escalation.reason}
                </div>

                <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
                  <Clock size={14} />
                  <span>{new Date(escalation.createdAt).toLocaleString()}</span>
                </div>

                {/* Conversation History */}
                {selectedEscalation?.id === escalation.id && escalation.history && escalation.history.length > 0 && (
                  <div className="mt-4 border-t pt-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">Conversation History</h4>
                    <div className="space-y-2 max-h-60 overflow-y-auto bg-gray-50 rounded-lg p-3">
                      {escalation.history.map((msg, idx) => (
                        <div 
                          key={idx} 
                          className={`flex gap-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`flex items-start gap-2 max-w-[80%] ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white flex-shrink-0 ${
                              msg.sender === 'user' ? 'bg-gray-500' : 'bg-sky-400'
                            }`}>
                              {msg.sender === 'user' ? <User size={12} /> : <Bot size={12} />}
                            </div>
                            <div className={`px-3 py-2 rounded-lg text-sm ${
                              msg.sender === 'user' 
                                ? 'bg-sky-400 text-white' 
                                : 'bg-white border border-gray-200 text-gray-700'
                            }`}>
                              {msg.text}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleResolve(escalation.id);
                  }}
                  className="mt-3 w-full flex items-center justify-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                >
                  <CheckCircle size={16} />
                  Mark as Resolved
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Sessions Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Active Sessions</h2>
        {sessions.length === 0 ? (
          <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 p-20 text-center">
            <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-6 border border-gray-200">
              <Monitor className="text-gray-400 w-10 h-10" />
            </div>
            <h3 className="text-xl font-semibold text-gray-700">No Active Sessions</h3>
            <p className="text-gray-400 mt-2">Waiting for users to establish connections...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <div key={session.id} className="bg-white rounded-lg border border-gray-200 p-4 hover:border-sky-400 transition-all">
                <div className="flex items-center align-center justify-between">
                  <div className={`p-2 rounded-lg ${session.type === 'voice' ? 'bg-sky-50 text-sky-500' : 'bg-emerald-50 text-emerald-500'}`}>
                    {session.type === 'voice' ? <Mic size={20} /> : <MessageSquare size={20} />}
                  </div>
                  <div className="text-right">
                    <span className={`inline-block px-3 py-1 rounded-lg text-xs font-medium uppercase tracking-wider
                      ${session.type === 'voice' ? 'bg-sky-100 text-sky-600' : 'bg-emerald-100 text-emerald-600'}
                    `}>
                      {session.type} Agent
                    </span>
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <div className="flex items-center gap-3 text-gray-600">
                    <Hash size={18} className="text-gray-400" />
                    <span className="font-mono text-sm font-medium truncate">{session.id}</span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-600">
                    <Clock size={18} className="text-gray-400" />
                    <span className="text-xs font-medium text-gray-400">
                      Connected: {new Date(session.startTime).toLocaleTimeString()}
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

