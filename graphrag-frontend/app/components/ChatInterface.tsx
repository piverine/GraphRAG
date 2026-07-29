'use client';

import React, { useState } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  subgraph?: any[];
}

interface ChatInterfaceProps {
  onSubgraphUpdate?: (subgraph: any[]) => void;
}

export default function ChatInterface({ onSubgraphUpdate }: ChatInterfaceProps) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am your GraphRAG Academic Assistant. Ask me any question about algorithms, lineage, datasets, or contradictions in your ingested literature.',
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userQuestion = query.trim();
    setQuery('');
    setMessages((prev) => [...prev, { role: 'user', content: userQuestion }]);
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:8000/query', { question: userQuestion });
      const answer = res.data.answer || 'No grounded answer returned.';
      const subgraph = res.data.subgraph || [];

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: answer, subgraph },
      ]);

      if (onSubgraphUpdate && subgraph.length > 0) {
        onSubgraphUpdate(subgraph);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ Failed to connect to backend. Please make sure FastAPI backend is running and GOOGLE_API_KEY is configured.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col h-[520px] shadow-xl overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
          <h2 className="text-sm font-semibold text-slate-200">Grounded Literature QA</h2>
        </div>
        <span className="text-xs text-slate-500 font-mono">Gemini 2.5 Flash + Neo4j</span>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg p-3 text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white rounded-br-none shadow-md'
                  : 'bg-slate-800 text-slate-200 border border-slate-700/50 rounded-bl-none shadow-sm'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.subgraph && msg.subgraph.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-700 text-[10px] text-cyan-300 font-mono">
                  📊 Subgraph facts attached ({msg.subgraph.length} records)
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/80 border border-slate-700/50 text-slate-400 rounded-lg p-3 text-xs flex items-center gap-2">
              <span className="w-3 h-3 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              Translating natural language to Cypher & synthesizing grounded facts...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800 bg-slate-950/80 flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask e.g. 'Which algorithms improve on BERT?'"
          className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}
