'use client';

import React, { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  confidence_score?: number;
}

export default function ChatInterface({ twinId }: { twinId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/chat/${twinId}?query=${encodeURIComponent(input)}`, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer YOUR_JWT_TOKEN', // In real app, get from auth state
        },
      });

      const data = await response.json();
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        confidence_score: data.confidence_score,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] w-full max-w-2xl border rounded-lg overflow-hidden bg-white shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-gray-800'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-2 text-xs text-gray-400">
                  Citations: {msg.citations.join(', ')}
                </div>
              )}
              {msg.confidence_score !== undefined && (
                <div className={`mt-1 text-[10px] ${msg.confidence_score < 0.7 ? 'text-red-500' : 'text-green-500'}`}>
                  Confidence: {(msg.confidence_score * 100).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-gray-400 text-sm italic">Thinking...</div>}
      </div>
      <div className="p-4 border-t flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask your digital twin..."
          className="flex-1 border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:bg-blue-300"
        >
          Send
        </button>
      </div>
    </div>
  );
}
