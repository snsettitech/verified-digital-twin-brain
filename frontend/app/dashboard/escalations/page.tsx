'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEscalations = async () => {
      try {
        const response = await fetch('http://localhost:8000/escalations', {
          headers: { 'Authorization': 'Bearer development_token' }
        });
        if (response.ok) {
          const data = await response.json();
          setEscalations(data);
        }
      } catch (error) {
        console.error('Error fetching escalations:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchEscalations();
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[#f8fafc] text-slate-900 font-sans">
      <header className="sticky top-0 z-10 bg-white border-b px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="text-xl font-black tracking-tighter text-blue-600 hover:opacity-80 transition-opacity">
            VT-BRAIN
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-slate-500 hover:text-slate-800">Chat</Link>
            <a href="#" className="text-sm font-medium text-slate-500 hover:text-slate-800">Knowledge Base</a>
            <Link href="/dashboard/escalations" className="text-sm font-bold text-blue-600 border-b-2 border-blue-600 pb-1">Escalations</Link>
            <a href="#" className="text-sm font-medium text-slate-500 hover:text-slate-800">Analytics</a>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full p-10">
        <h1 className="text-3xl font-extrabold tracking-tight mb-8">Escalations Queue</h1>
        
        {loading ? (
          <div className="flex justify-center p-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : escalations.length === 0 ? (
          <div className="bg-white p-20 rounded-3xl border border-dashed flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-green-50 text-green-500 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h3 className="text-lg font-bold text-slate-800">No open escalations</h3>
            <p className="text-slate-500 max-w-sm mt-2">All low-confidence answers have been reviewed or the system is performing with high confidence.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {escalations.map((esc) => (
              <div key={esc.id} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${
                      esc.status === 'open' ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-green-50 text-green-600'
                    }`}>
                      {esc.status}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {new Date(esc.created_at).toLocaleString()}
                    </span>
                  </div>
                  <button className="text-blue-600 text-xs font-bold hover:underline">Review & Reply</button>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Low Confidence Answer</div>
                    <div className="text-sm bg-slate-50 p-4 rounded-xl border border-slate-100 italic text-slate-600">
                      "{esc.messages?.content}"
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Confidence Score</div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden max-w-xs">
                      <div 
                        className="bg-red-500 h-full" 
                        style={{ width: `${(esc.messages?.confidence_score || 0) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-[10px] font-bold text-red-600 mt-1">
                      {(esc.messages?.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
