'use client';

import React, { useState } from 'react';
import ChatInterface from '../../components/Chat/ChatInterface';

export default function DashboardPage() {
  const [activeTwin, setActiveTwin] = useState('twin-123'); // Default for demo

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Digital Twin Brain</h1>
            <p className="text-gray-500">Monitor and interact with your verified knowledge base.</p>
          </div>
          <div className="flex gap-4">
            <button className="bg-white border px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
              Source Management
            </button>
            <button className="bg-white border px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50">
              Escalations
            </button>
          </div>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h2 className="text-xl font-semibold mb-4">Chat with Twin</h2>
              <ChatInterface twinId={activeTwin} />
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h2 className="text-xl font-semibold mb-4">Trust Analytics</h2>
              <div className="space-y-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-100">
                  <div className="text-sm text-green-800 font-medium">Average Confidence</div>
                  <div className="text-2xl font-bold text-green-900">92.4%</div>
                </div>
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-100">
                  <div className="text-sm text-yellow-800 font-medium">Open Escalations</div>
                  <div className="text-2xl font-bold text-yellow-900">5</div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <h2 className="text-xl font-semibold mb-4">Recent Sources</h2>
              <ul className="space-y-3">
                {['company_handbook.pdf', 'product_specs_v2.pdf', 'meeting_notes_dec.pdf'].map((s, i) => (
                  <li key={i} className="flex justify-between items-center text-sm">
                    <span className="text-gray-700">{s}</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-[10px] rounded-full uppercase font-bold">Processed</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
