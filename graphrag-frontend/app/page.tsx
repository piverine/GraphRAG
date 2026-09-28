'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getApiBaseUrl } from './config';
import UploadInterface from './components/UploadInterface';
import ChatInterface from './components/ChatInterface';
import GraphVisualizer from './components/GraphVisualizer';
import HeadlineFeatures from './components/HeadlineFeatures';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'headline'>('chat');
  const [subgraph, setSubgraph] = useState<any[]>([]);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [dbStats, setDbStats] = useState<{ node_count: number; relationship_count: number }>({
    node_count: 0,
    relationship_count: 0,
  });

  const fetchStats = async () => {
    try {
      const apiBase = getApiBaseUrl();
      const res = await axios.get(`${apiBase}/graph/summary`, { timeout: 3000 });
      setDbStats(res.data);
      setBackendOnline(true);
    } catch (err) {
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      {/* Header Bar */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center font-bold text-slate-950 text-lg shadow-lg shadow-indigo-500/20">
            G
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 leading-none">GraphRAG Academic Explorer</h1>
            <p className="text-[11px] text-slate-400 mt-1">Literature Mapping with Gemini 2.5 Flash & Neo4j</p>
          </div>
        </div>

        {/* Database Stats & Backend Connectivity Pill */}
        <div className="flex items-center gap-4 bg-slate-900 border border-slate-800 rounded-full px-4 py-1.5 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                backendOnline === true
                  ? 'bg-emerald-400 animate-pulse'
                  : backendOnline === false
                  ? 'bg-rose-500'
                  : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-400">Backend:</span>
            <span
              className={`font-semibold ${
                backendOnline === true ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {backendOnline === true ? 'Online' : backendOnline === false ? 'Offline (Run main.py)' : 'Checking...'}
            </span>
          </div>
          <div className="w-px h-3 bg-slate-800" />
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Nodes:</span>
            <span className="text-emerald-400 font-semibold">{dbStats.node_count}</span>
          </div>
          <div className="w-px h-3 bg-slate-800" />
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Edges:</span>
            <span className="text-cyan-400 font-semibold">{dbStats.relationship_count}</span>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 max-w-[1600px] w-full mx-auto">
        {/* Left Column: Interactive Controls */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {/* Navigation Tabs */}
          <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'chat' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Grounded Chat
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'upload' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Paper Ingestion
            </button>
            <button
              onClick={() => setActiveTab('headline')}
              className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === 'headline' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Headline Queries
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'chat' && <ChatInterface onSubgraphUpdate={(sg) => setSubgraph(sg)} />}
          {activeTab === 'upload' && <UploadInterface onIngestComplete={fetchStats} />}
          {activeTab === 'headline' && <HeadlineFeatures onSubgraphUpdate={(sg) => setSubgraph(sg)} />}
        </div>

        {/* Right Column: Dynamic Graph Visualizer */}
        <div className="lg:col-span-7 flex flex-col bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
          <div className="flex justify-between items-center mb-3 px-2">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Live Subgraph Fact Visualizer
            </h2>
            <span className="text-[11px] text-slate-500 font-mono">Traceable Knowledge Graph</span>
          </div>

          <div className="flex-1 w-full h-full min-h-[500px]">
            <GraphVisualizer subgraph={subgraph} />
          </div>
        </div>
      </div>
    </main>
  );
}
