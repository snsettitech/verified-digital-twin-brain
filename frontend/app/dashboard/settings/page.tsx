'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function SettingsPage() {
  const [twinId, setTwinId] = useState('eeeed554-9180-4229-a9af-0f8dd2c69e9b');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [twinData, setTwinData] = useState({
    name: '',
    description: '',
    settings: {
      system_prompt: ''
    }
  });

  const fetchTwinData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/twins/${twinId}`, {
        headers: { 'Authorization': 'Bearer development_token' }
      });
      if (response.ok) {
        const data = await response.json();
        setTwinData({
          name: data.name || '',
          description: data.description || '',
          settings: {
            system_prompt: data.settings?.system_prompt || ''
          }
        });
      }
    } catch (error) {
      console.error('Error fetching twin data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTwinData();
  }, [twinId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await fetch(`http://localhost:8000/twins/${twinId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer development_token'
        },
        body: JSON.stringify(twinData)
      });

      if (response.ok) {
        alert('Twin settings updated successfully!');
      } else {
        const error = await response.json();
        alert(`Update failed: ${error.detail || 'Server error'}`);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to connect to backend.');
    } finally {
      setSaving(false);
    }
  };

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
            <Link href="/dashboard/escalations" className="text-sm font-medium text-slate-500 hover:text-slate-800">Escalations</Link>
            <Link href="/dashboard/settings" className="text-sm font-bold text-blue-600 border-b-2 border-blue-600 pb-1">Settings</Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full p-10">
        <h1 className="text-3xl font-extrabold tracking-tight mb-8">Twin Settings</h1>

        {loading ? (
          <div className="flex justify-center p-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <form onSubmit={handleSave} className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm space-y-6">
            <div>
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Twin Name</label>
              <input
                type="text"
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                value={twinData.name}
                onChange={(e) => setTwinData({ ...twinData, name: e.target.value })}
                placeholder="e.g., Personal Assistant Twin"
              />
            </div>

            <div>
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Description</label>
              <textarea
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all resize-none"
                rows={2}
                value={twinData.description}
                onChange={(e) => setTwinData({ ...twinData, description: e.target.value })}
                placeholder="Briefly describe what this twin represents..."
              />
            </div>

            <div>
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">System Prompt (Personality)</label>
              <textarea
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all resize-none"
                rows={8}
                value={twinData.settings.system_prompt}
                onChange={(e) => setTwinData({ 
                  ...twinData, 
                  settings: { ...twinData.settings, system_prompt: e.target.value } 
                })}
                placeholder="Define how your twin should behave and respond..."
              />
              <p className="text-[10px] text-slate-400 mt-2 italic">
                Tip: Describe the twin's tone, expertise level, and any specific constraints.
              </p>
            </div>

            <div className="flex justify-end pt-4">
              <button
                type="submit"
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white text-xs font-bold py-3 px-10 rounded-xl transition-all shadow-md shadow-blue-100 flex items-center gap-2"
              >
                {saving ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    Saving Changes...
                  </>
                ) : 'Update Twin Memory'}
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
