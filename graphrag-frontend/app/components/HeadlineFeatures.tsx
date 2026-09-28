'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { getApiBaseUrl } from '../config';

interface HeadlineFeaturesProps {
  onSubgraphUpdate?: (subgraph: any[]) => void;
}

export default function HeadlineFeatures({ onSubgraphUpdate }: HeadlineFeaturesProps) {
  const [activeTab, setActiveTab] = useState<'lineage' | 'contradictions' | 'gaps'>('lineage');
  const [algorithm, setAlgorithm] = useState('Attention');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runLineage = async () => {
    setLoading(true);
    try {
      const apiBase = getApiBaseUrl();
      const res = await axios.get(`${apiBase}/headline/lineage?alg_id=${encodeURIComponent(algorithm)}`, { timeout: 30000 });
      setData(res.data);
    } catch (err: any) {
      setData({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const runContradictions = async () => {
    setLoading(true);
    try {
      const apiBase = getApiBaseUrl();
      const res = await axios.get(`${apiBase}/headline/contradictions`, { timeout: 30000 });
      setData(res.data);
    } catch (err: any) {
      setData({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const runGaps = async () => {
    setLoading(true);
    try {
      const apiBase = getApiBaseUrl();
      const res = await axios.get(`${apiBase}/headline/gaps`, { timeout: 30000 });
      setData(res.data);
    } catch (err: any) {
      setData({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <h2 className="text-lg font-semibold text-slate-100 mb-1 flex items-center gap-2">
        <span className="text-indigo-400">⚡</span> Headline Graph Traversal Queries
      </h2>
      <p className="text-xs text-slate-400 mb-4">
        Execute verified, multi-hop Cypher queries directly against the graph database.
      </p>

      <div className="flex gap-2 border-b border-slate-800 pb-3 mb-4">
        <button
          onClick={() => { setActiveTab('lineage'); setData(null); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${activeTab === 'lineage' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}
        >
          1. Lineage Tracing
        </button>
        <button
          onClick={() => { setActiveTab('contradictions'); setData(null); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${activeTab === 'contradictions' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}
        >
          2. Contradiction Finder
        </button>
        <button
          onClick={() => { setActiveTab('gaps'); setData(null); }}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${activeTab === 'gaps' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}
        >
          3. Gap Analysis
        </button>
      </div>

      {activeTab === 'lineage' && (
        <div className="space-y-3">
          <p className="text-xs text-slate-300">
            Traces multi-hop <code className="text-indigo-400 bg-slate-950 px-1 py-0.5 rounded">IMPROVES*1..5</code> paths transitively across algorithms.
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              placeholder="Base Algorithm (e.g. Attention, BERT)"
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 flex-1"
            />
            <button
              onClick={runLineage}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-xs font-medium"
            >
              {loading ? 'Running...' : 'Trace Lineage'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'contradictions' && (
        <div className="space-y-3">
          <p className="text-xs text-slate-300">
            Discovers symmetric <code className="text-indigo-400 bg-slate-950 px-1 py-0.5 rounded">CONTRADICTS</code> relationships with source paper provenance.
          </p>
          <button
            onClick={runContradictions}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-xs font-medium"
          >
            {loading ? 'Running...' : 'Find Contradictions'}
          </button>
        </div>
      )}

      {activeTab === 'gaps' && (
        <div className="space-y-3">
          <p className="text-xs text-slate-300">
            Ranks <code className="text-indigo-400 bg-slate-950 px-1 py-0.5 rounded">Concept</code> nodes by lowest connection degree to surface under-explored topics.
          </p>
          <button
            onClick={runGaps}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-xs font-medium"
          >
            {loading ? 'Running...' : 'Analyze Gaps'}
          </button>
        </div>
      )}

      {data && (
        <div className="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono overflow-x-auto max-h-48 text-slate-300">
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
