'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  confidence_score?: number;
}

/**
 * ChatInterface Component
 * 
 * The primary interface for interacting with a Digital Twin. 
 * Supports streaming responses, conversation history, and real-time confidence/citation display.
 * 
 * @param twinId - The UUID of the digital twin being queried.
 * @param conversationId - Optional existing conversation UUID to load history.
 * @param onConversationStarted - Callback when a new conversation is initialized by the backend.
 */
export default function ChatInterface({ 
  twinId, 
  conversationId, 
  onConversationStarted 
}: { 
  twinId: string;
  conversationId?: string | null;
  onConversationStarted?: (id: string) => void;
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I am your Verified Digital Twin. Ask me anything about your uploaded documents.",
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Fetches and loads message history for a given conversation.
   * If no conversationId is provided, resets to the initial greeting.
   */
  useEffect(() => {
    const loadHistory = async () => {
      if (!conversationId) {
        setMessages([{
          role: 'assistant',
          content: "Hello! I am your Verified Digital Twin. Ask me anything about your uploaded documents.",
        }]);
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/conversations/${conversationId}/messages`, {
          headers: { 'Authorization': 'Bearer development_token' }
        });
        if (response.ok) {
          const data = await response.json();
          const history = data.map((m: any) => ({
            role: m.role,
            content: m.content,
            citations: m.citations,
            confidence_score: m.confidence_score
          }));
          setMessages(history.length > 0 ? history : [{
            role: 'assistant',
            content: "Hello! I am your Verified Digital Twin. Ask me anything about your uploaded documents.",
          }]);
        }
      } catch (error) {
        console.error('Error loading history:', error);
      }
    };
    loadHistory();
  }, [conversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  /**
   * Sends a user query to the backend and processes the streaming NDJSON response.
   * 
   * Flow:
   * 1. Add user message to UI.
   * 2. Start streaming request to /chat/{twinId}.
   * 3. Parse NDJSON chunks (metadata -> content -> done).
   * 4. Update the last assistant message in real-time.
   */
  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // Create a placeholder for the assistant message
    const assistantMsg: Message = {
      role: 'assistant',
      content: '',
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const url = new URL(`http://localhost:8000/chat/${twinId}`);

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer development_token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          conversation_id: conversationId || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${response.status}`);
      }

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const data = JSON.parse(line);
              if (data.type === 'metadata') {
                if (data.conversation_id && !conversationId && onConversationStarted) {
                  onConversationStarted(data.conversation_id);
                }
                setMessages((prev) => {
                  const last = [...prev];
                  const lastMsg = { ...last[last.length - 1] };
                  lastMsg.confidence_score = data.confidence_score;
                  lastMsg.citations = data.citations;
                  last[last.length - 1] = lastMsg;
                  return last;
                });
              } else if (data.type === 'content') {
                setMessages((prev) => {
                  const last = [...prev];
                  const lastMsg = { ...last[last.length - 1] };
                  lastMsg.content += data.content;
                  last[last.length - 1] = lastMsg;
                  return last;
                });
              }
            } catch (e) {
              console.error('Error parsing stream line:', e);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      let errorMessage = "Sorry, I'm having trouble connecting to my brain right now.";
      if (error.message?.includes('Failed to fetch')) {
        errorMessage = "Could not connect to the backend server. Please ensure the FastAPI server is running on port 8000.";
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }
      setMessages((prev) => {
        const last = [...prev];
        last[last.length - 1] = { 
          role: 'assistant', 
          content: errorMessage
        };
        return last;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Chat Header */}
      <div className="px-6 py-4 bg-slate-50 border-b flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <div>
            <div className="font-bold text-slate-800">Verified Twin</div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Ready to assist</span>
            </div>
          </div>
        </div>
        <div className="text-xs font-medium text-slate-400 bg-white px-3 py-1 rounded-full border">
          ID: {twinId}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[#fcfcfd]">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              {/* Avatar Icon */}
              <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center text-xs font-bold ${
                msg.role === 'user' ? 'bg-indigo-100 text-indigo-600' : 'bg-blue-100 text-blue-600'
              }`}>
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>

              <div className="space-y-2">
                <div className={`p-4 rounded-2xl shadow-sm border ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white border-blue-500 rounded-tr-none' 
                    : 'bg-white text-slate-800 border-slate-100 rounded-tl-none'
                }`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>

                {/* Citations & Confidence (Assistant Only) */}
                {msg.role === 'assistant' && (msg.citations || msg.confidence_score !== undefined) && (
                  <div className="flex flex-wrap gap-2 px-1">
                    {msg.confidence_score !== undefined && (
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-bold border uppercase ${
                        msg.confidence_score > 0.8 
                          ? 'bg-green-50 text-green-700 border-green-100' 
                          : msg.confidence_score > 0.5 
                            ? 'bg-yellow-50 text-yellow-700 border-yellow-100'
                            : 'bg-red-50 text-red-700 border-red-100'
                      }`}>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                        Confidence: {(msg.confidence_score * 100).toFixed(0)}%
                      </div>
                    )}
                    {msg.citations?.map((source, sIdx) => (
                      <div key={sIdx} className="bg-slate-100 text-slate-600 px-2 py-1 rounded-md text-[10px] font-bold border border-slate-200 uppercase flex items-center gap-1">
                        <svg className="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                        Source {sIdx + 1}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start animate-pulse">
            <div className="flex gap-3 max-w-[85%]">
              <div className="w-8 h-8 rounded-full bg-slate-100 shrink-0"></div>
              <div className="bg-white p-4 rounded-2xl border border-slate-100 text-slate-400 text-sm">
                Searching documents...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t">
        <div className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask a question about your documents..."
            className="w-full bg-slate-100 border-none rounded-xl px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all pr-24"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="absolute right-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            <span>Ask</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </div>
        <p className="mt-3 text-[10px] text-center text-slate-400 font-medium tracking-wide uppercase">
          Verified answers only. hallucination prevention enabled.
        </p>
      </div>
    </div>
  );
}
